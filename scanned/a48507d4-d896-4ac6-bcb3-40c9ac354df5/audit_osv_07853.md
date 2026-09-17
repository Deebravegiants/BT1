# [M] Possible request smuggling in HTTP/2 due missing validation

## Summary
Severity: Medium
Advisory: BIT-zookeeper-2021-21295
Aliases: CVE-2021-21295, GHSA-wm47-8v5p-wjpj
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-zookeeper-2021-21295
Type: osv

## Affected
- Bitnami: `zookeeper` — affected >=3.5.9 <3.5.10

## Details
Netty is an open-source, asynchronous event-driven network application framework for rapid development of maintainable high performance protocol servers & clients. In Netty (io.netty:netty-codec-http2) before version 4.1.60.Final there is a vulnerability that enables request smuggling. If a Content-Length header is present in the original HTTP/2 request, the field is not validated by `Http2MultiplexHandler` as it is propagated up. This is fine as long as the request is not proxied through as HTTP/1.1. If the request comes in as an HTTP/2 stream, gets converted into the HTTP/1.1 domain objects (`HttpRequest`, `HttpContent`, etc.) via `Http2StreamFrameToHttpObjectCodec `and then sent up to the child channel's pipeline and proxied through a remote peer as HTTP/1.1 this may result in request smuggling. In a proxy case, users may assume the content-length is validated somehow, which is not the case. If the request is forwarded to a backend channel that is a HTTP/1.1 connection, the Content-Length now has meaning and needs to be checked. An attacker can smuggle requests inside the body as it gets downgraded from HTTP/2 to HTTP/1.1. For an example attack refer to the linked GitHub Advisory. Users are only affected if all of this is true: `HTTP2MultiplexCodec` or `Http2FrameCodec` is used, `Http2StreamFrameToHttpObjectCodec` is used to convert to HTTP/1.1 objects, and these HTTP/1.1 objects are forwarded to another remote peer. This has been patched in 4.1.60.Final As a workaround, the user can do the validation by themselves by implementing a custom `ChannelInboundHandler` that is put in the `ChannelPipeline` behind `Http2StreamFrameToHttpObjectCodec`.

## References
- https://github.com/Netflix/zuul/pull/980
- https://github.com/netty/netty/commit/89c241e3b1795ff257af4ad6eadc616cb2fb3dc4
- https://github.com/netty/netty/security/advisories/GHSA-wm47-8v5p-wjpj
- https://lists.apache.org/thread.html/r02e467123d45006a1dda20a38349e9c74c3a4b53e2e07be0939ecb3f%40%3Cdev.ranger.apache.org%3E
- https://lists.apache.org/thread.html/r040a5e4d9cca2f98354b58a70b27099672276f66995c4e2e39545d0b%40%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r04a3e0d9f53421fb946c60cc54762b7151dc692eb4e39970a7579052%40%3Ccommits.servicecomb.apache.org%3E
- https://lists.apache.org/thread.html/r0b09f3e31e004fe583f677f7afa46bd30110904576c13c5ac818ac2c%40%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r15f66ada9a5faf4bac69d9e7c4521cedfefa62df9509881603791969%40%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r16c4b55ac82be72f28adad4f8061477e5f978199d5725691dcc82c24%40%3Ccommits.servicecomb.apache.org%3E
- https://lists.apache.org/thread.html/r1908a34b9cc7120e5c19968a116ddbcffea5e9deb76c2be4fa461904%40%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r1bca0b81193b74a451fc6d687ab58ef3a1f5ec40f6c61561d8dd9509%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r22adb45fe902aeafcd0a1c4db13984224a667676c323c66db3af38a1%40%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r22b2f34447d71c9a0ad9079b7860323d5584fb9b40eb42668c21eaf1%40%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r268850f26639ebe249356ed6d8edb54ee8943be6f200f770784fb190%40%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r27b7e5a588ec826b15f38c40be500c50073400019ce7b8adfd07fece%40%3Cissues.hbase.apache.org%3E
- https://lists.apache.org/thread.html/r2936730ef0a06e724b96539bc7eacfcd3628987c16b1b99c790e7b87%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r2e93ce23e04c3f0a61e987d1111d0695cb668ac4ec4edbf237bd3e80%40%3Ccommits.servicecomb.apache.org%3E
- https://lists.apache.org/thread.html/r312ce5bd3c6bf08c138349b507b6f1c25fe9cf40b6f2b0014c9d12b1%40%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r32b0b640ad2be3b858f0af51c68a7d5c5a66a462c8bbb93699825cd3%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r33eb06b05afbc7df28d31055cae0cb3fd36cab808c884bf6d680bea5%40%3Cdev.zookeeper.apache.org%3E
