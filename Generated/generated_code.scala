```scala
// Simple Key Exchange protocol in B2Scala
// Based on KB examples: Needham-Schroeder public key protocol, Otway-Rees protocols

import scala.collection.mutable

object Client extends Agent {
  // Initial message to Server with nonceC
  def tellInitialMessage = tell(ClientHello(nonceC))

  // Expected messages from Server
  var expectedMessagesFromServer = mutable.Set.empty[SI_Term]

  // Process received messages from Server
  def processReceivedMessages: SI_Term = {
    for (msg <- expectedMessagesFromServer) {
      msg match {
        case ServerHello(nonceS, cert) =>
          val sessionKey = encrypt3(nonceC, nonceS, cert)
          tell(Finished(encrypt2(sessionKey)))
        case _ => // TODO handle invalid messages
      }
    }
  }

  // Agent definition with initial message and processing of received messages
  def apply: BSC_Agent = {
    Agent { (tellInitialMessage || processReceivedMessages) }
  }
}

object Server extends Agent {
  // Expected initial message from Client
  var expectedInitialMessageFromClient = mutable.Set.empty[SI_Term]

  // Process received initial message from Client and generate response
  def processReceivedInitialMessage: SI_Term = {
    val msg = expectedInitialMessageFromClient.head
    msg match {
      case ClientHello(nonceC) =>
        val nonceS = Token(nonceS)
        val cert = Token(cert)
        tell(ServerHello(nonceS, cert))
    }
  }

  // Agent definition with processing of received initial message and generation of response
  def apply: BSC_Agent = {
    Agent { (processReceivedInitialMessage) }
  }
}

// Define protocol messages as Scala classes
case class ClientHello(nonceC: SI_Term) extends SI_Term
case class ServerHello(nonceS: SI_Term, cert: SI_Term) extends SI_Term
case class Finished(mac: SI_Term) extends SI_Term

// Utility functions for encryption and token generation
def encrypt2(n: SI_Term, k: SI_Term): SI_Term = // implementation not shown
def encrypt3(n: SI_Term, x: SI_Term, k: SI_Term): SI_Term = // implementation not shown
def Token(x: Any): SI_Term = // implementation not shown
```