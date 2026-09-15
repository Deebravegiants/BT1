# [M] Wallos: SSRF via url parameter leading to File Traversal

## Summary
Severity: Medium
Advisory: CVE-2026-30828
Aliases: GHSA-p7qj-669r-grvc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-07
Source: https://osv.dev/vulnerability/CVE-2026-30828
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. Prior to version 4.6.2, the url parameter can be used to retrieve local system files. This issue has been patched in version 4.6.2.

## References
- https://github.com/ellite/Wallos/releases/tag/v4.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30828.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-p7qj-669r-grvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-30828
- https://github.com/ellite/Wallos/commit/e8a513591dbbf885966e2ef55c38622785b9060d
