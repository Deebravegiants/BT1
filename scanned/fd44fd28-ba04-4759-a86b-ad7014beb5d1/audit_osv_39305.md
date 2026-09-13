# [H] OpenSIPS: SIP Message Smuggling via TCP Content-Length Integer Overflow

## Summary
Severity: High
Advisory: CVE-2026-45103
Aliases: GHSA-jv35-555v-54jh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-45103
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. In versions prior to 3.6.6 and 4.0.0-rc1, the TCP message framing layer parses the Content-Length header using unsigned int arithmetic with no overflow check. When an attacker sends a Content-Length value that overflows unsigned int (e.g., 4294967296), the framing layer computes a wrapped-around value (e.g., 0) and splits the TCP stream at the wrong boundary, causing the body of the first SIP message to be processed as a separate message and enabling SIP message smuggling. Because Content-Length is parsed in the transport layer before authentication, an unauthenticated, network-based attacker can smuggle arbitrary SIP messages over any TCP-based transport (proto_tcp, proto_tls, proto_ws, proto_wss) on any instance with TCP enabled, with no routing-script preconditions. This allows smuggled messages to bypass front-end SBC/proxy security policies, inherit the connection's authentication context, and evade rate limiting. This issue has been fixed in versions 3.6.6 and 4.0.0-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45103.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-jv35-555v-54jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45103
- https://github.com/OpenSIPS/opensips/commit/4d23613b
- https://github.com/OpenSIPS/opensips/commit/5f103eff
