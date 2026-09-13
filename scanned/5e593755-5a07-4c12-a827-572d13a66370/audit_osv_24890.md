# [M] OpenSIPS has vulnerability in the Digest Authentication Parser

## Summary
Severity: Medium
Advisory: CVE-2023-28098
Aliases: GHSA-jrqg-vppj-hr2h
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-28098
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Prior to versions 3.1.7 and 3.2.4, a specially crafted Authorization header causes OpenSIPS to crash or behave in an unexpected way due to a bug in the function `parse_param_name()` . This issue was discovered while performing coverage guided fuzzing of the function parse_msg. The AddressSanitizer identified that the issue occurred in the function `q_memchr()` which is being called by the function `parse_param_name()`. This issue may cause erratic program behaviour or a server crash. It affects configurations containing
functions that make use of the affected code, such as the function `www_authorize()` . Versions 3.1.7 and 3.2.4 contain a fix.

## References
- https://opensips.org/pub/audit-2022/opensips-audit-technical-report-full.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28098.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-jrqg-vppj-hr2h
- https://nvd.nist.gov/vuln/detail/CVE-2023-28098
- https://github.com/OpenSIPS/opensips/commit/dd9141b6f67d7df4072f3430f628d4b73df5e102
