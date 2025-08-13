```scala
// Simple Key Exchange Protocol

import scala.language.implicitConversions

// Agents
case class Client() extends Agent {}
case class Server() extends Agent {}

// Messages
case class ClientHello(nonceC: SI_Term) extends SI_Term
case class ServerHello(nonceS: SI_Term, cert: SI_Term) extends SI_Term
case class Finished(MAC: SI_Term) extends SI_Term

// Protocol implementation
object SimpleKeyExchange {
  def clientProtocol(client: Client, server: Server): CalledAgent = {
    val nonceC = Token("nonceC")
    client tell (ClientHello(nonceC)) || server ask (ServerHello _, _) map { case (nonceS, cert) =>
      val sessionKey = encrypt2(nonceC, nonceS)
      // TODO: mutual authentication
      client tell (Finished(sessionKey))
    }
  }

  def serverProtocol(server: Server): CalledAgent = {
    val nonceS = Token("nonceS")
    val cert = Token("cert") // TODO: load server certificate
    server tell (ServerHello(nonceS, cert)) || ask _ map { case ClientHello(nonceC) =>
      val sessionKey = encrypt2(nonceC, nonceS)
      // TODO: mutual authentication
      server tell (Finished(sessionKey))
    }
  }
}
```

Note that some assumptions are left as TODOs, as they were not explicitly mentioned in the draft.