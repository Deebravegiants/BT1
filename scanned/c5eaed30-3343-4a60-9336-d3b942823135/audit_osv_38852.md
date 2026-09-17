# [M] Netty: HTTP Request Smuggling due to malformed Transfer-Encoding

## Summary
Severity: Medium
Advisory: CVE-2026-42585
Aliases: GHSA-38f8-5428-x5cv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-42585
Type: osv

## Details
Netty is an asynchronous, event-driven network application framework. Prior to 4.2.13.Final and 4.1.133.Final, Netty incorrectly parses malformed Transfer-Encoding, enabling request smuggling attacks. This vulnerability is fixed in 4.2.13.Final and 4.1.133.Final.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42585.json
- https://github.com/netty/netty/security/advisories/GHSA-38f8-5428-x5cv
- https://nvd.nist.gov/vuln/detail/CVE-2026-42585
