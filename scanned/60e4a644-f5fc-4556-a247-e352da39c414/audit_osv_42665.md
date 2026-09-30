# [C] Apache Allura: Server-side request forgery

## Summary
Severity: Critical
Advisory: CVE-2026-69223
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-69223
Type: osv

## Details
Apache Allura's webhooks are vulnerable to Server-Side Request Forgery (SSRF).

This issue affects Apache Allura: before 1.19.1.

Users are recommended to upgrade to version 1.19.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/11/4
- https://allura.apache.org/posts/2026-allura-1.19.1.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69223.json
- https://lists.apache.org/thread/9xpltfm6nombd7rdrx5o0hh8kxmm82pb
- https://nvd.nist.gov/vuln/detail/CVE-2026-69223
