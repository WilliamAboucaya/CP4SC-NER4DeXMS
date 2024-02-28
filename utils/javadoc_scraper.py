"""
Code obtained from https://github.com/jerrytheo/jdoc-scraper and partially modified.

Copyright (C) Abhijit J. Theophilus, abhitheo96@gmail.com
"""

import os
import re
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Lock
from xml.dom import minidom
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


def scrape_package(package_name, package_url):
    """Handles one package. It retrieves the web page, calculates the number of
    classes to parse, sequentially tries to retrieve each class' web page and
    parse it for its name, description, and methods.  This information is stored
    in an XML file named <package_name>.xml.
    """

    log_path = os.path.join('logs', package_name + '.log')
    if os.path.isfile(log_path):
        os.remove(log_path)

    print_lock = Lock()

    try:
        # Get package page. Construct soup. Store package name and
        # description.

        package_page = requests.get(package_url)
        package_soup = BeautifulSoup(package_page.text, 'lxml')

        docSumm = package_soup.find(class_='docSummary')
        if docSumm:
            desc = docSumm.div.text
            desc = ' '.join(desc.split())
        else:
            desc = None
        package_info = {
            'name': package_name,
            'description': desc
        }

        # Classes are in a <table> captioned 'Class Summary'. Each
        # class is represented by a row in the table, where the
        # first column is its name and the last one is its
        # description.

        span = package_soup.find('span', string='Class Summary')
        if span:
            tbl = span.parent.parent
        else:
            return 'empty'
        cls_list = tbl.find_all('tr')[1:]           # First row is headers.

    except Exception:
        with print_lock:
            print("failure")
        raise

    else:
        successes = 0
        package_info['classes'] = []

        # Each class is parsed on one of 32 threads.
        nthreads = 32 if len(cls_list) >= 32 else len(cls_list)
        executor = ThreadPoolExecutor(nthreads)
        for cls_ in cls_list:
            cls_info = dict()
            try:
                # Name.
                cls_name = package_name + '.' \
                         + cls_.find('td', 'colFirst').a.text
                cls_info['name'] = cls_name
                # Description.
                desc_tag = cls_.find('div', 'block')
                if desc_tag:
                    cls_info['description'] = ' '.join(desc_tag.text.split())
                else:
                    cls_info['description'] = None
                # Methods.
                cls_url = get_absolute_url(package_url, cls_.find('td', 'colFirst').a['href'])
                cls_page = requests.get(cls_url)
                cls_soup = BeautifulSoup(cls_page.text, 'lxml')
                future = executor.submit(scrape_class, cls_soup, cls_name)
                cls_info['methods'] = future.result()
            except Exception as exc:
                with open(log_path, 'a') as log_file:
                    log_file.write('%s:%s\n' % (cls_name, str(exc)))
            else:
                successes += 1
                package_info['classes'].append(cls_info)
        executor.shutdown()

        if successes == len(cls_list):
            status = "SUCCESS"
        elif successes == 0:
            status = "FAILURE"
        else:
            status = "PARTIAL"

        write_xml(package_info)

        with print_lock:
            if status == "SUCCESS":
                print('success')
            else:
                print('partial')

        return package_info


def parse_parameters(row):
    """Returns the parameters of the class as a dict of the form,
    parameter_type: parameter_label from its corresponding <tr> in the
    documentation <table>.
    """

    td = row.find(class_='colLast')
    if not td:
        td = row.find(class_='colOne')

    # Matches the patterns specified as
    # (<group 1>)<some data>(<group 2>); thereby capturing the same
    # parameters from two different positions in the line.
    # group 1 -- captured from the link to method detail. Contains the
    #            class name in full.
    # group 2 -- captured from the text. Contains the parameter name.
    pregex = re.compile(r'\(([^)]+)\).*\(([^)]+)\)')
    td = ' '.join(str(i) for i in td.contents if str(i) != '\n')
    pmatch = re.search(pregex, td)
    if pmatch:
        # %20 is a space in HTTP requests.
        ptypes = pmatch.group(1).split('%20')

        # Need to get every alternate element. e.g. 'a' from 'int a'.
        pnames = BeautifulSoup(pmatch.group(2), 'lxml').body.text.split()
        pnames = [pnames[i] for i in range(1, len(pnames), 2)]

        # After the regex capture, both may have ,'s if not the last
        # parameter in the prototype.
        pdict = {key.strip(','): value.strip(',') for key, value in zip(pnames, ptypes)}
        return pdict
    else:
        return


def parse_return_type(row):

    """Get the return type of the class from its corresponding <tr> in
    the documentation <table>.
    """

    # Methods declared private, protected or abstract are never
    # available to the user.
    _disallowed = ('private', 'protected' 'abstract')

    ret = row.find(class_='colFirst').get_text()
    if [i for i in ret.split() if i in _disallowed]:
        return
    ret = ret.split()[-1]
    return None if ret == 'void' else ret


def scrape_class(soup, cls_name):
    """Parse the Class description page. Saves info regarding
    constructors and class methods."""

    methods = []

    span = soup.find('span', string='Methods')
    # Not all classes have methods.
    if span:
        tbl = span.parent.parent
        for row in tbl.find_all('tr')[1:]:
            # Check if method is not deprecated.
            inner = row.find('td', class_='colLast')
            if inner.div:
                descr = ' '.join(inner.div.get_text().split())
                if 'Deprecated' in descr:
                    continue
            else:
                descr = None

            # Store metadata.
            name = inner.code.strong.a.text
            method_info = {
                'name': name,
                'description': descr,
                'parameters': parse_parameters(row),
                'return': parse_return_type(row),
                }
            methods.append(method_info)

    # Handling constructors as follows,
    #   Return type -- Class name.
    #   Parameters  -- As specified.
    #   Name        -- Class name.
    #   Description -- As specified.

    span = soup.find('span', string='Constructors')
    # Not all classes have constructors.
    if span:
        tbl = span.parent.parent
        for row in tbl.find_all('tr')[1:]:
            # Check if constructor deprecated.
            inner = row.find('td', class_='colOne')
            if not inner:
                inner = row.find('td', class_='colFirst')
                if 'protected' in inner.text or 'private' in inner.text:
                    continue
                inner = row.find('td', class_='colLast')

            if inner.div:
                descr = ' '.join(inner.div.get_text().split())
                if 'Deprecated' in descr:
                    continue
            else:
                descr = None

            # Store metadata
            construct_info = {
                'name': cls_name,
                'description': descr,
                'parameters': parse_parameters(row),
                'return': cls_name,
                }
            methods.append(construct_info)

    # Save all inherited functions for a future implementation.
    inherited = {}
    name_re = re.compile('methods_inherited_from_class_(.*)')
    for a in soup.find_all('a'):
        if not a.has_attr('name'):
            continue
        name_mch = re.match(name_re, a['name'])
        if not name_mch:
            continue
        inherited[name_mch.group(1)] = a.parent.code.text.split(', ')

    return {'methods': methods, 'inherited': inherited}


def get_absolute_url(current_url, relative_url):
    """Returns the absolute url given the current url and the url
    relative to the current url.
    """

    current_url = current_url.split('/')
    relative_url = relative_url.split('/')

    # Number of levels to go up.
    levels = relative_url.count('..')

    abs_url = '/'.join(current_url[: -(levels+1)]) + '/' + '/'.join(relative_url[levels:])
    return abs_url


def write_xml(package_info):
    """Write the package info to an xml file.
    The xml is structured as follows,

    package
      ├── name
      ├── description
      ├── class (id)
      │     ├── name
      │     └── description
      └── method (id)
            ├── name
            ├── description
            ├── parameter
            │     ├── name
            │     └── type
            ├── return
            └── class

    The bracketed terms indicate attributes.
    """
    root = ET.Element('package')

    # Name.
    name = ET.SubElement(root, 'name')
    name.text = package_info['name']

    # Description.
    desc = ET.SubElement(root, 'desc')
    desc.text = package_info['description']

    # Classes.
    cls_id = 0
    mtd_id = 0
    for class_ in package_info['classes']:
        cls = ET.SubElement(root, 'class')

        # Class ID.
        cls.set('id', str(cls_id))
        cls_id = cls_id + 1

        # Class name.
        cls_name = ET.SubElement(cls, 'name')
        cls_name.text = class_['name']

        # Class description.
        cls_desc = ET.SubElement(cls, 'description')
        cls_desc.text = class_['description']

    for class_ in package_info['classes']:
        for method in class_['methods']['methods']:
            mtd = ET.SubElement(root, 'method')

            # Method ID.
            mtd.set('id', str(mtd_id))
            mtd_id = mtd_id + 1

            # Method name.
            mtd_name = ET.SubElement(mtd, 'name')
            mtd_name.text = method['name']

            # Method description.
            mtd_desc = ET.SubElement(mtd, 'description')
            mtd_desc.text = method['description']

            # Method parameters.
            prm_id = 0
            if method['parameters']:
                for param in method['parameters']:
                    prm = ET.SubElement(mtd, 'parameter')
                    prm.set('id', str(prm_id))
                    prm_id = prm_id + 1

                    prm_name = ET.SubElement(prm, 'name')
                    prm_name.text = param

                    prm_type = ET.SubElement(prm, 'type')
                    prm_type.text = method['parameters'][param]

            # Method return type.
            if method['return']:
                mtd_retn = ET.SubElement(mtd, 'return')
                mtd_retn.text = method['return']

            # Method class.
            mtd_clsn = ET.SubElement(mtd, 'class')
            mtd_clsn.text = class_['name']

    # Prettify the xml to double space indentation.
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    xml_path = os.path.join('../resources/javadoc', package_info['name'] + '.xml')
    with open(xml_path, 'w') as xml_file:
        xml_file.write(reparsed.toprettyxml(indent='  '))


if __name__ == "__main__":
    packages = {
        "org.eclipse.californium.core": "https://javadoc.io/static/org.eclipse.californium/californium-core/3.10.0/org/eclipse/californium/core/package-summary.html",
        "org.eclipse.paho.client.mqttv3": "https://eclipse.dev/paho/files/javadoc/org/eclipse/paho/client/mqttv3/package-summary.html",
        "org.apache.http": "https://hc.apache.org/httpcomponents-core-4.4.x/current/httpcore/apidocs/org/apache/http/package-summary.html",
        "org.apache.http.client.methods": "https://javadoc.io/static/org.apache.httpcomponents/httpclient/4.5.3/org/apache/http/client/methods/package-summary.html",
        "org.apache.http.impl.client": "https://javadoc.io/static/org.apache.httpcomponents/httpclient/4.5.3/org/apache/http/impl/client/package-summary.html",
        # "": "",
    }

    futures = {}
    # Each package is parsed on one of 8 processes.
    with ProcessPoolExecutor(8) as executor:
        for key in packages:
            name = key
            url = packages[key]
            futures[name] = executor.submit(scrape_package, name, url)

    success = 0
    partial = 0
    failure = 0
    empties = 0
    with open('pkg_retry', 'w') as rf:
        for name in futures:
            try:
                result = futures[name].result()
                if result == 'success':
                    success += 1
                elif result == 'partial':
                    rf.write(name + '\n')
                    partial += 1
                elif result == 'empty':
                    empties += 1
            except Exception:
                rf.write(name + '\n')
                failure += 1

    print('\nTotal packages:', success + partial + failure + empties, 'packages')
    print('Complete:', success, 'packages')
    print('Incomplete:', partial, 'packages')
    print('Failed:', failure, 'packages')
    print('Empty:', empties, 'packages')
