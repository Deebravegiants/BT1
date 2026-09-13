# [H] Apache CXF: Denial of service via message header attachments

## Summary
Severity: High
Advisory: CVE-2026-64958
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-64958
Type: osv

## Details
An incomplete fix for CVE-2026-50645 means that it is still possible to perform a denial of service attack on Apache CXF by sending a message with many attachment headers. Users are recommended to upgrade to versions 4.2.3 or 4.1.8 or 3.6.12, which fix this issue.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64958.json
- https://lists.apache.org/thread/trsnkxc2f21585zlt819blvchgl6oykb
- https://nvd.nist.gov/vuln/detail/CVE-2026-64958
