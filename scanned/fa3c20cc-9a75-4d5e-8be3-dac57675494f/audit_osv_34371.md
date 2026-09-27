# [M] InstantCMS vulnerable to Server-Side Request Forgery via package installer

## Summary
Severity: Medium
Advisory: CVE-2025-59055
Aliases: GHSA-79hh-mhvg-whrw
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-59055
Type: osv

## Details
InstantCMS is a free and open source content management system. A blind Server-Side Request Forgery (SSRF) vulnerability in InstantCMS up to and including 2.17.3 allows authenticated remote attackers to make nay HTTP/HTTPS request via the package parameter. It is possible to make any HTTP/HTTPS request to any website in installer functionality. Due to such vulnerability it is possible to for example scan local network, call local services and its functions, conduct a DoS attack, and/or disclose a server's real IP if it's behind a reverse proxy. It is also possible to exhaust server resources by sending plethora of such requests. As of time of publication, no patched releases are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59055.json
- https://github.com/instantsoft/icms2/security/advisories/GHSA-79hh-mhvg-whrw
- https://nvd.nist.gov/vuln/detail/CVE-2025-59055
- https://github.com/instantsoft/icms2/commit/fa997bdab3429fad0c850966bfacbcb96d5ab041
