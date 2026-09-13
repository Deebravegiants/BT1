# [M] H2O alllows bypassing address-based access control with 0-RTT

## Summary
Severity: Medium
Advisory: CVE-2024-45397
Aliases: GHSA-jf2c-xjcp-wg4c
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-11
Source: https://osv.dev/vulnerability/CVE-2024-45397
Type: osv

## Details
h2o is an HTTP server with support for HTTP/1.x, HTTP/2 and HTTP/3. When an HTTP request using TLS/1.3 early data on top of TCP Fast Open or QUIC 0-RTT packets is received and the IP-address-based access control is used, the access control does not detect and prohibit HTTP requests conveyed by packets with a spoofed source address. This behavior allows attackers on the network to execute HTTP requests from addresses that are otherwise rejected by the address-based access control. The vulnerability has been addressed in commit 15ed15a. Users may disable the use of TCP FastOpen and QUIC to mitigate the issue.

## References
- https://h2o.examp1e.net/configure/http3_directives.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45397.json
- https://github.com/h2o/h2o/security/advisories/GHSA-jf2c-xjcp-wg4c
- https://nvd.nist.gov/vuln/detail/CVE-2024-45397
- https://github.com/h2o/h2o/commit/15ed15a2efb83a77bb4baaa5a119e639c2f6898a
