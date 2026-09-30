# [H] Web http client: Unchecked Server-Side Malicious Packet Issue

## Summary
Severity: High
Advisory: CVE-2025-55085
Aliases: GHSA-9c77-rgp9-c2g2
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/CVE-2025-55085
Type: osv

## Details
In NextX Duo before 6.4.4, in the HTTP client module, the network support code for Eclipse Foundation ThreadX, the parsing of HTTP header fields was missing bounds verification. A crafted server response could cause undefined behavior.

## References
- https://github.com/eclipse-threadx/netxduo/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55085.json
- https://github.com/eclipse-threadx/netxduo/security/advisories/GHSA-9c77-rgp9-c2g2
- https://nvd.nist.gov/vuln/detail/CVE-2025-55085
