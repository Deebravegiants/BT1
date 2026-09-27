# [M] Apache Answer: The custom avatar was not properly validated

## Summary
Severity: Medium
Advisory: CVE-2026-34031
Aliases: GHSA-x4f6-mqg6-28xx, GO-2026-6154
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-34031
Type: osv

## Details
Unrestricted Upload of File with Dangerous Type vulnerability in Apache Answer.

This issue affects Apache Answer: through 2.0.0.

The server did not sufficiently validate user-supplied image URLs, allowing arbitrary external content to be embedded as profile images, which could expose users to unintended external requests and tracking by third-party servers.
Users are recommended to upgrade to version 2.0.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/09/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34031.json
- https://lists.apache.org/thread/rwtxy39t54to9kv3dqtbjsbdpyk4jkd2
- https://nvd.nist.gov/vuln/detail/CVE-2026-34031
