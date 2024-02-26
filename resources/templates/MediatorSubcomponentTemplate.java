package org.zefxis.dexms.dex.protocols.primitives;

import java.util.List;

import org.zefxis.dexms.dex.protocols.Manageable;
import org.zefxis.dexms.dex.protocols.observers.MediatorSubComponentObserver;
import org.zefxis.dexms.gmdl.utils.Data;
import org.zefxis.dexms.gmdl.utils.GmServiceRepresentation;
import org.zefxis.dexms.gmdl.utils.MediatorConfiguration;
import org.zefxis.dexms.gmdl.utils.Scope;


public class Mediator{protocol_name}Subcomponent extends MediatorGmSubcomponent {{

  protected MediatorGmSubcomponent nextComponent;
  protected GmServiceRepresentation serviceRepresentation;
  protected final MediatorConfiguration bcConfiguration;
  protected MediatorSubComponentObserver subComponentObserver;

  public MediatorGmSubcomponent(MediatorConfiguration bcConfiguration) {{
	  System.out.println("MediatorGmSubcomponent");
    this.bcConfiguration = bcConfiguration;
  }}

  public void registerObserver(String name){{
	  System.out.println("registerObserver");
	  this.subComponentObserver = new MediatorSubComponentObserver(name);
  }}


  public void setNextComponent(MediatorGmSubcomponent nextComponent) {{
	  System.out.println(nextComponent.toString());
    this.nextComponent = nextComponent;
  }}

  public abstract void setGmServiceRepresentation(GmServiceRepresentation serviceRepresentation);

  public abstract GmServiceRepresentation getGmServiceRepresentation();

  /* ------ one-way Sender ------ */

  /**
   * Method used for an one-way communication initialized by a sender.
   *
   * Using this method a sender sends some data to the peer of the destination
   * IP address without expecting any response.
   *
   * @param destination the IP address of the peer we wish to communicate
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param data the data we want to send which are type of class Data
   * @param lease for how long the data sent will be valid
   */
  public abstract void postOneway(final String destination, final Scope scope, final List<Data<?>> data, final long lease);
  /* ------ One-way Receiver ------ */

  /**
   * Method used for an one-way communication initialized by a receiver.
   *
   * Using this method a receiver is waiting multiple data to a specific scope.
   *
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param exchange exchange object
   */
  public abstract void mgetOneway(final Scope scope, final Object exchange);

  /**
   * Method used for an one-way communication initialized by a receiver.
   *
   * Using this method a receiver is waiting multiple data to a specific scope by an exclusive source (sender).
   *
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param source the IP address of the exclusive sender
   * @param exchange exchange object
   */
  public abstract void xmgetOneway(final String source, final Scope scope, final Object exchange);

  /* ------ Two-way Client-Synchronous ------ */

  /**
   * Method used for an two-way synchronous communication initialized by a client.
   *
   * Using this method a client sends some data to the peer of the destination
   * IP address and is waiting until receiving a response.
   *
   * @param destination the IP address of the peer we wish to communicate
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param datas the data we want to send which are type of class Data
   * @param lease for how long the data sent will be valid. In this case must be 0
   * @param <T> generic type
   * @return
   */

  public abstract <T> T postTwowaySync(final String destination, final Scope scope, final List<Data<?>> datas, final long lease);

  /**
   * Method used for a two-way synchronous communication initialized by a client. (uncorrelated at the middleware layer)
   *
   * Using this method a client is waiting (response) data for a timeout limited period to a specific scope by the exclusive destination (server).
   *
   * @param destination the IP address of the exclusive destination (server)
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param timeout the time the server is waiting for the response
   * @param response response object
   *
   */
  public abstract void xtgetTwowaySync(final String destination, final Scope scope, final long timeout, final Object response);

  /* ------ Two-way Server-Synchronous ------ */

  /**
   * Method used for an two-way synchronous communication initialized by a server.
   *
   * Using this method a server is waiting multiple data to a specific scope.
   *
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param exchange exchange object
   * @param <T> generic type
   * @return
   */

  public abstract <T> T mgetTwowaySync(final Scope scope, final Object exchange);

  /**
   * Method used for an two-way synchronous communication initialized by a server.
   *
   * Using this method a server sends the response to the source (client)
   *
   * @param source the IP address of the peer we wish to communicate
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param data the data we want to send which are type of class Data
   * @param lease for how long the data sent will be valid. In this case must be 0
   * @param exchange
   */
  //  public void postBackTwowaySync(String source, Scope scope, Data data, long lease, Object exchange);

  /* ------ Two-way Client-Asynchronous ------ */

  /**
   * Method used for an two-way asynchronous communication initialized by a client.
   *
   * Using this method a client sends some data to the peer of the destination
   * IP address without waiting for a response. postTwowayAsync can be performed again
   * without a response of the previous.
   *
   * @param destination the IP address of the peer we wish to communicate
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param data the data we want to send which are type of class Data
   * @param lease for how long the data sent will be valid
   */
  public abstract void postTwowayAsync(final String destination, final Scope scope, final List<Data<?>> data, final long lease);

  /**
   * Method used for a two-way asynchronous communication initialized by a client.
   *
   * Using this method a client will receive (response) data asynchronously to a specific scope by the exclusive destination (server).
   *
   * @param destination the IP address of the exclusive destination (server)
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param response
   */
  public abstract void xgetTwowayAsync(final String destination, final Scope scope, final Object response);

  /* ------ Two-way Server-Asynchronous ------ */

  /**
   * Method used for an two-way asynchronous communication initialized by a server.
   *
   * Using this method a server is waiting multiple data to a specific scope.
   *
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param exchange
   */
  public abstract void mgetTwowayAsync(final Scope scope, final Object exchange);

  /**
   * Method used for an two-way asynchronous communication initialized by a server.
   *
   * Using this method a server sends the response to the source (client)
   *
   * @param source the IP address of the peer we wish to communicate
   * @param scope the identifier of the corresponding operation (SOAP), or resource (REST, CoAP), or topic (Pub/Sub), or stream, or template (Tuplespace)
   * @param data the data we want to send which are type of class Data
   * @param lease for how long the data sent will be valid
   * @param exchange
   */
  public abstract void postBackTwowayAsync(final String source, final Scope scope, final Data<?> data, final long lease, final Object exchange);

  /* ------ Stream Consumer ------ */

  /* ------ Stream Producer ------ */



  /**
   * Method use to send notification on start one-way/two-way synchronous/asynchronous communication call
   */
  public void notifyStartEvent(){{

	  this.subComponentObserver.update("start");
  }}

  /**
   * Method use to send notification on release one-way/two-way synchronous/asynchronous communication call
   */
  public void notifyReleaseEvent(){{

	  this.subComponentObserver.update("release");
  }}
}}