I will generate the B2Scala code based on the provided draft and examples. Here is the resulting code:

```scala
// Simple Key Exchange Protocol

import b2scala.primitives._

object Client {
  def clientHello(nonceC: String): Message = 
    get ( message(client, server, initial("client_id", "domain_name", "protocol_version", client_hello(nonceC))) )

  def finished(MAC: String): Message = 
    get ( message(client, server, finished("label_finished", prf(MAC, "label_finished"))) )
}

object Server {
  def serverHello(nonceS: String, cert: String): Message = 
    tell( message(server, client, handshake(cert, "protocol_version", sign(sig_scope(cert), skServer), pkServer)) ) *
    tell( server_begin_quic(pkServer, kdf(dh(cert, nonceS), "label_quic"), "client_id", "domain_name") )

  def mutualAuth(nonceA: String, certB: String): Message = 
    message(client, server, initial("client_id", "domain_name", "protocol_version", client_hello(nonceA))) *
    message(server, client, handshake(certB, "protocol_version", sign(sig_scope(certB), skServer), pkServer)) *
    message(client, server, finished(prf(kdf(dh(certB, nonceS), "label_quic"), "label_finished")))
}

// Message Flow

tell( Server.serverHello("nonce_S_1", "cert_B") ) * // Server Hello
Client.clientHello("nonce_C_2") * // Client Hello
Server.mutualAuth("nonce_A_3", "cert_B") // Mutual Auth
```

This code assumes that the necessary imports and definitions (e.g., `message`, `get`, `tell`, etc.) are already available in the B2Scala library. The provided code follows the message flow described in the draft, using the Bach primitives for message exchange.