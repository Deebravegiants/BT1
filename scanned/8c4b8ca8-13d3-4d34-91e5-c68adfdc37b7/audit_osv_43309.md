# [M] Apache Allura: Missing permission checks IDOR

## Summary
Severity: Medium
Advisory: CVE-2026-73239
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73239
Type: osv

## Details
Insecure Direct Object Reference (IDOR) due to missing permission checks for multiple Artifact types in Apache Allura.

This issue affects Apache Allura: before 1.19.1.

Users are recommended to upgrade to version 1.19.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/18
- https://allura.apache.org/posts/2026-allura-1.19.1.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73239.json
- https://lists.apache.org/thread/ryn6yomo897d43ovrd47g02t8ycmbxb3
- https://nvd.nist.gov/vuln/detail/CVE-2026-73239
