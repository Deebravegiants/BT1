# [H] OpenSIPS has vulnerability in the parse_uri() function

## Summary
Severity: High
Advisory: CVE-2023-27597
Aliases: GHSA-358f-935m-7p9c
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-27597
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Prior to versions 3.1.8 and 3.2.5, when a specially crafted SIP message is processed by the function `rewrite_ruri`, a crash occurs due to a segmentation fault. This issue causes the server to crash. It affects configurations containing functions that make use of the affected code, such as the function `setport`. This issue has been fixed in version 3.1.8 and 3.2.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27597.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-358f-935m-7p9c
- https://nvd.nist.gov/vuln/detail/CVE-2023-27597
- https://github.com/OpenSIPS/opensips/commit/b2dffe4b5cd81182c9c8eabb6c96aac96c7acfe3
