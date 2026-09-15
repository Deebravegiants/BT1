# [H] OpenSIPS has vulnerability in the parse_via() function

## Summary
Severity: High
Advisory: CVE-2023-27598
Aliases: GHSA-wxfg-3gwh-rhvx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-27598
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Prior to versions 3.1.7 and 3.2.4, sending a malformed `Via` header to OpenSIPS triggers a segmentation fault when the function `calc_tag_suffix` is called. A specially crafted `Via` header, which is deemed correct by the parser, will pass uninitialized strings to the function `MD5StringArray` which leads to the crash. Abuse of this vulnerability leads to Denial of Service due to a crash. Since the uninitialized string points to memory location `0x0`, no further exploitation appears to be possible. No special network privileges are required to perform this attack, as long as the OpenSIPS configuration makes use of functions such as `sl_send_reply` or `sl_gen_totag` that trigger the vulnerable code. This issue has been fixed in versions 3.1.7 and 3.2.4.

## References
- https://opensips.org/pub/audit-2022/opensips-audit-technical-report-full.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27598.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-wxfg-3gwh-rhvx
- https://nvd.nist.gov/vuln/detail/CVE-2023-27598
- https://github.com/OpenSIPS/opensips/commit/ab611f74f69d9c42be5401c40d56ea06a58f5dd7
