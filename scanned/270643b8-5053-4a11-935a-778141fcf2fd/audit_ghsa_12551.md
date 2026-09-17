# [M] netty-handler SniHandler 16MB allocation

## Summary
Severity: Medium
Advisory: GHSA-6mjq-h674-j845
CVE: CVE-2023-34462
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-6mjq-h674-j845
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=0 <4.1.94.Final

## Details
### Summary
The `SniHandler` can allocate up to 16MB of heap for each channel during the TLS handshake. When the handler or the channel does not have an idle timeout, it can be used to make a TCP server using the `SniHandler` to allocate 16MB of heap.

### Details
The `SniHandler` class is a handler that waits for the TLS handshake to configure a `SslHandler` according to the indicated server name by the `ClientHello` record. For this matter it allocates a `ByteBuf` using the value defined in the `ClientHello` record. 

Normally the value of the packet should be smaller than the handshake packet but there are not checks done here and the way the code is written, it is possible to craft a packet that makes the `SslClientHelloHandler`

1/ allocate a 16MB `ByteBuf`
2/ not fail `decode` method `in` buffer
3/ get out of the loop without an exception

The combination of this without the use of a timeout makes  easy to connect to a TCP server and allocate 16MB of heap memory per connection.

### Impact
If the user has no idle timeout handler configured it might be possible for a remote peer to send a client hello packet which lead the server to buffer up to 16MB of data per connection. This could lead to a OutOfMemoryError and so result in a DDOS.

## References
- https://github.com/netty/netty/security/advisories/GHSA-6mjq-h674-j845
- https://nvd.nist.gov/vuln/detail/CVE-2023-34462
- https://github.com/netty/netty/commit/535da17e45201ae4278c0479e6162bb4127d4c32
- https://github.com/netty/netty
- https://security.netapp.com/advisory/ntap-20230803-0001
- https://security.netapp.com/advisory/ntap-20240621-0007
- https://www.debian.org/security/2023/dsa-5558
