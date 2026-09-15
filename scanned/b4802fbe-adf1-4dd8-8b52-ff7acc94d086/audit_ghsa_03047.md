# [H] Unbounded connection acceptance leads to file handle exhaustion

## Summary
Severity: High
Advisory: GHSA-xmw9-q7x9-j5qc
CVE: CVE-2021-21293
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-02-02
Source: https://github.com/advisories/GHSA-xmw9-q7x9-j5qc
Type: github-advisory

## Affected
- Maven: `org.http4s:blaze-core_2.11` — affected >=0 <0.14.15
- Maven: `org.http4s:blaze-core_2.12` — affected >=0 <0.14.15
- Maven: `org.http4s:blaze-core_2.13` — affected >=0 <0.14.15

## Details
### Impact

All servers running blaze-core <= 0.14.14, including blaze-http and http4s-blaze-server users, are affected.

Blaze, accepts connections unconditionally on a dedicated thread pool. This has the net effect of amplifying degradation in services that are unable to handle their current request load, since incoming connections are still accepted and added to an unbounded queue. Each connection allocates a socket handle, which drains a scarce OS resource. This can also confound higher level circuit breakers which work based on detecting failed connections.

The vast majority of affected users are using it as part of http4s-blaze-server <= 0.21.16.  http4s provides a mechanism for limiting open connections, but is enforced inside the Blaze accept loop, after the connection is accepted and the socket opened. Thus, the limit only prevents the number of connections which can be simultaneously processed, not the number of connections which can be held open.

### Patches

The issue is fixed in version 0.14.15 for `NIO1SocketServerGroup`.  A `maxConnections` parameter is added, with a default value of 512.  Concurrent connections beyond this limit are rejected.  To run unbounded, which is not recommended, set a negative number.

The `NIO2SocketServerGroup`  has no such setting and is now deprecated.

### Workarounds
* An Nginx side-car acting as a reverse proxy for the local http4s-blaze-server instance would be able to apply a connection limiting semantic before the sockets reach blaze-core. Nginx’s connection bounding is both asynchronous and properly respects backpressure.
* A similar sidecar strategy is viable for other non-HTTP services running on blaze-core.
* http4s-ember-server is an alternative to http4s-blaze-server, but does not yet have HTTP/2 or web socket support.  Its performance in terms of RPS is appreciably behind Blaze’s, and as the newest backend, has substantially less industrial uptake.
* http4s-jetty is an alternative to http4s-blaze-server, but does not yet have web socket support.  Its performance in terms of requests per second is somewhat behind Blaze’s, and despite Jetty's industrial adoption, the http4s integration has substantially less industrial uptake.
* http4s-tomcat is an alternative to http4s-blaze-server, but does not yet have HTTP/2 web socket support.  Its performance in terms of requests per second is somewhat behind Blaze’s, and despite Jetty's industrial adoption, the http4s integration has substantially less industrial uptake.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [http4s/blaze](http://github.com/http4s/blaze)
* Contact us according to the [http4s security policy](https://github.com/http4s/http4s/security/policy)

## References
- https://github.com/http4s/blaze/security/advisories/GHSA-xmw9-q7x9-j5qc
- https://github.com/http4s/http4s/security/advisories/GHSA-xhv5-w9c5-2r2w
- https://nvd.nist.gov/vuln/detail/CVE-2021-21293
- https://github.com/http4s/blaze/commit/4f786177f9fb71ab272f3a5f6c80bca3e5662aa1
