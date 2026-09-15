# [H] OpenSIPS has vulnerability in the parse_to_param() function

## Summary
Severity: High
Advisory: CVE-2023-27599
Aliases: GHSA-qvj2-vqrg-f5jx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-27599
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Prior to versions 3.1.7 and 3.2.4, when the function `append_hf` handles a SIP message with a malformed To header, a call to the function `abort()` is performed, resulting in a crash. This is due to the following check in `data_lump.c:399` in the function `anchor_lump`. An attacker abusing this vulnerability will crash OpenSIPS leading to Denial of Service. It affects configurations containing functions that make use of the affected code, such as the function `append_hf`. This issue has been fixed in versions 3.1.7 and 3.2.4.

## References
- https://opensips.org/pub/audit-2022/opensips-audit-technical-report-full.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27599.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-qvj2-vqrg-f5jx
- https://nvd.nist.gov/vuln/detail/CVE-2023-27599
- https://github.com/OpenSIPS/opensips/commit/cb56694d290530ac308f44b453c18120b1c1109d
