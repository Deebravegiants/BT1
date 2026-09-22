# [M] CVE-2024-33667

## Summary
Severity: Medium
Advisory: CVE-2024-33667
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-26
Source: https://osv.dev/vulnerability/CVE-2024-33667
Type: osv

## Details
An issue was discovered in Zammad before 6.3.0. An authenticated agent could perform a remote Denial of Service attack by calling an endpoint that accepts a generic method name, which was not properly sanitized against an allowlist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33667.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33667
- https://zammad.com/en/advisories/zaa-2024-03
