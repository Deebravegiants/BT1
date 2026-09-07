# [H] Connection leaking on idle timeout when TCP congested

## Summary
Severity: High
Advisory: GHSA-rggv-cv7r-mw98
CVE: CVE-2024-22201
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-26
Source: https://github.com/advisories/GHSA-rggv-cv7r-mw98
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=9.3.0 <9.4.54
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=10.0.0 <10.0.20
- Maven: `org.eclipse.jetty.http3:http3-common` — affected >=10.0.8 <10.0.20
- Maven: `org.eclipse.jetty.http2:http2-common` — affected >=11.0.0 <11.0.20
- Maven: `org.eclipse.jetty.http3:http3-common` — affected >=11.0.8 <11.0.20
- Maven: `org.eclipse.jetty.http2:jetty-http2-common` — affected >=12.0.0 <12.0.6
- Maven: `org.eclipse.jetty.http3:jetty-http3-common` — affected >=12.0.0 <12.0.6

## Details
### Impact
If an HTTP/2 connection gets TCP congested, when an idle timeout occurs the HTTP/2 session is marked as closed, and then a GOAWAY frame is queued to be written.
However it is not written because the connection is TCP congested.
When another idle timeout period elapses, it is then supposed to hard close the connection, but it delegates to the HTTP/2 session which reports that it has already been closed so it does not attempt to hard close the connection.

This leaves the connection in ESTABLISHED state (i.e. not closed), TCP congested, and idle.

An attacker can cause many connections to end up in this state, and the server may run out of file descriptors, eventually causing the server to stop accepting new connections from valid clients.

The client may also be impacted (if the server does not read causing a TCP congestion), but the issue is more severe for servers.

### Patches
Patched versions:
* 9.4.54
* 10.0.20
* 11.0.20
* 12.0.6

### Workarounds
Disable HTTP/2 and HTTP/3 support until you can upgrade to a patched version of Jetty.
HTTP/1.x is not affected.

### References
* https://github.com/jetty/jetty.project/issues/11256.

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-rggv-cv7r-mw98
- https://nvd.nist.gov/vuln/detail/CVE-2024-22201
- https://github.com/jetty/jetty.project/issues/11256
- https://github.com/jetty/jetty.project/issues/11259
- https://github.com/jetty/jetty.project/commit/0839a208cdc3fcfe25206a77af59ba9fda260188
- https://github.com/jetty/jetty.project/commit/b953871c9a5ff4fbca4a2499848f75182dbd9810
- https://github.com/jetty/jetty.project
- https://lists.debian.org/debian-lts-announce/2024/04/msg00002.html
- https://security.netapp.com/advisory/ntap-20240329-0001
- http://www.openwall.com/lists/oss-security/2024/03/20/2
