# [M] Quadratic complexity may lead to a denial of service in cmark-gfm

## Summary
Severity: Medium
Advisory: CVE-2023-24824
Aliases: GHSA-66g8-4hjf-77xh, HSEC-2025-0007
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-03-31
Source: https://osv.dev/vulnerability/CVE-2023-24824
Type: osv

## Details
cmark-gfm is GitHub's fork of cmark, a CommonMark parsing and rendering library and program in C. A polynomial time complexity issue in cmark-gfm may lead to unbounded resource exhaustion and subsequent denial of service. This CVE covers quadratic complexity issues when parsing text which leads with either large numbers of `>` or `-` characters. This issue has been addressed in version 0.29.0.gfm.10. Users are advised to upgrade. Users unable to upgrade should validate that their input comes from trusted sources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24824.json
- https://github.com/github/cmark-gfm/security/advisories/GHSA-66g8-4hjf-77xh
- https://nvd.nist.gov/vuln/detail/CVE-2023-24824
- https://github.com/github/cmark-gfm/commit/2300c1bd2c8226108885bf019655c4159cf26b59
