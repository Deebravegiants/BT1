# [M] MongoDB client C Driver may infinitely loop when validating certain BSON input data

## Summary
Severity: Medium
Advisory: CVE-2023-0437
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-0437
Type: osv

## Details
When calling bson_utf8_validate on some inputs a loop with an exit condition that cannot be reached may occur, i.e. an infinite loop. This issue affects All MongoDB C Driver versions prior to versions 1.25.0.

## References
- https://jira.mongodb.org/browse/CDRIVER-4747
- https://lists.debian.org/debian-lts-announce/2025/05/msg00012.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7GUVOAFZFSYTNBF6R7H4XJM5DHWBRQ6P/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0437.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0437
