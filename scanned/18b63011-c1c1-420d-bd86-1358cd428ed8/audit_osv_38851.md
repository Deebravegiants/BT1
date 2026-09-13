# [M] Netty: HTTP Request Smuggling due to incorrect chunk size parsing

## Summary
Severity: Medium
Advisory: CVE-2026-42580
Aliases: GHSA-m4cv-j2px-7723
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-42580
Type: osv

## Details
Netty is an asynchronous, event-driven network application framework. Prior to 4.2.13.Final and 4.1.133.Final, Netty's chunk size parser silently overflows int, enabling request smuggling attacks. This vulnerability is fixed in 4.2.13.Final and 4.1.133.Final.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42580.json
- https://github.com/netty/netty/security/advisories/GHSA-m4cv-j2px-7723
- https://nvd.nist.gov/vuln/detail/CVE-2026-42580
