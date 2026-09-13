# [H] OpenSIPS has vulnerability in the Content-Length Parser

## Summary
Severity: High
Advisory: CVE-2023-28097
Aliases: GHSA-c6j5-f4h4-2xrq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-28097
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Prior to versions 3.1.9 and 3.2.6, a malformed SIP message containing a large _Content-Length_ value and a specially crafted Request-URI causes a segmentation fault in OpenSIPS. This issue occurs when a large amount of shared memory using the `-m` flag was allocated to OpenSIPS, such as 10 GB of RAM. On the test system, this issue occurred when shared memory was set to `2362` or higher. This issue is fixed in versions 3.1.9 and 3.2.6. The only workaround is to guarantee that the Content-Length value of input messages is never larger than `2147483647`.

## References
- https://opensips.org/pub/audit-2022/opensips-audit-technical-report-full.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28097.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-c6j5-f4h4-2xrq
- https://nvd.nist.gov/vuln/detail/CVE-2023-28097
- https://github.com/OpenSIPS/opensips/commit/7cab422e2fc648f910abba34f3f0dbb3ae171ff5
