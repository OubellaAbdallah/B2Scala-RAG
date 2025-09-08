Here is the Scala file:

```scala
package bscala.bsc_program

import bscala.bsc_data._
import bscala.bsc_agent._
import bscala.bsc_runner._
import bscala.bsc_settings._
import bscala.bsc_formula._

/**
 * A Simple Key Exchange Protocol
 */

object BSC_modelling_SimpleKeyExchangeProtocol {

  // DATA section
  case class ClientHello(nonceC: SI_Term, cert: SI_Term) extends DataMessage {
    override def toString = s"ClientHello($nonceC, $cert)"
  }

  case class ServerHello(nonceS: SI_Term, cert: SI_Term) extends DataMessage {
    override def toString = s"ServerHello($nonceS, $cert)"
  }

  case class Finished(mac: SI_Term) extends DataMessage {
    override def toString = s"Finished($mac)"
  }

  // AGENTS section
  trait ClientAgent extends AgentScript {
    self =>
    val name: String = "Client"
    var nonceC: SI_Term = _
    var cert: SI_Term = _

    // ClientHello message
    def clientHello(msg: DataMessage): ScriptStep = tell(ClientHello(nonceC, cert))
  }

  trait ServerAgent extends AgentScript {
    self =>
    val name: String = "Server"
    var nonceS: SI_Term = _
    var cert: SI_Term = _

    // ServerHello message
    def serverHello(msg: DataMessage): ScriptStep = tell(ServerHello(nonceS, cert))
  }

  // FORMULA & EXEC section
  object KeyExchangeFormula extends Formula {
    val id: String = "KeyExchange"
    override def toString = s"($id)"

    def keyEstablishment(clientNonce: SI_Term, serverNonce: SI_Term, serverPubKey: SI_Term): Formula =
      Token("SharedSecret") +:= (clientNonce ^ serverNonce) * serverPubKey

    def sessionKeyDerivation(sharedSecret: SI_Term): Formula = {
      // assumption: a hash function is used to derive the session key
      // NOTE: in B2Scala, we assume that the hash function is not explicitly defined
      //       but can be modeled using the ^ operator (as a placeholder)
      Token("SessionKey") +:= sharedSecret ^ ^ "HashFunction"
    }

    def finishedMessage(mac: SI_Term): Formula = {
      // assumption: the MAC is computed over all previous messages in the handshake
      // NOTE: in B2Scala, we assume that the Message Authentication Code (MAC) is
      //       modeled using a simple concatenation operator (+)
      Token("Finished") +:= mac + "+" + "HandshakeMessages"
    }
  }

  def keyExchangeProtocol: Protocol = {
    val clientAgent = new ClientAgent()
    val serverAgent = new ServerAgent()

    new Protocol {
      override def id: String = "SimpleKeyExchange"

      // step 1: ClientHello
      def step1(): ScriptStep = clientAgent.clientHello(ClientHello("nonceC", "cert"))

      // step 2: ServerHello
      def step2(): ScriptStep = serverAgent.serverHello(ServerHello("nonceS", "cert"))

      // step 3: KeyEstablishment (client)
      def step3(clientNonce: SI_Term, serverNonce: SI_Term): ScriptStep = clientAgent.keyEstablishment(clientNonce, serverNonce, "serverPubKey")

      // step 4: SessionKeyDerivation
      def step4(sharedSecret: SI_Term): ScriptStep = {
        val sessionKey = KeyExchangeFormula.sessionKeyDerivation(sharedSecret)
        tell(sessionKey)
      }

      // step 5: FinishedMessage (client)
      def step5(mac: SI_Term): ScriptStep = clientAgent.finishedMessage(mac)

      override def initialAgents(): Seq[Agent] = List(clientAgent, serverAgent)

      override def formula(): Formula = KeyExchangeFormula
    }
  }

  object runner {
    def main(args: Array[String]): Unit = {
      val protocol = keyExchangeProtocol
      val F = new BSC_Formula() with KeyExchangeFormula
      new BSC_Runner_BHM().execute(protocol, F)
    }
  }
}
```