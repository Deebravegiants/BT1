# [M] matrix-hookshot has a Potential Denial of Service when Hookshot is configured with GitHub support

## Summary
Severity: Medium
Advisory: CVE-2025-23197
Aliases: GHSA-cr4q-jf47-3645
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-27
Source: https://osv.dev/vulnerability/CVE-2025-23197
Type: osv

## Details
matrix-hookshot is a Matrix bot for connecting to external services like GitHub, GitLab, JIRA, and more. When Hookshot 6 version 6.0.1 or below, or Hookshot 5 version 5.4.1 or below, is configured with GitHub support, it is vulnerable to a Denial of Service (DoS) whereby it can crash on restart due to a missing check. The impact is greater to you untrusted users can add their own GitHub organizations to Hookshot in order to connect their room to a repository. This vulnerability is fixed in 6.0.2 and 5.4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23197.json
- https://github.com/matrix-org/matrix-hookshot/security/advisories/GHSA-cr4q-jf47-3645
- https://nvd.nist.gov/vuln/detail/CVE-2025-23197
- https://github.com/matrix-org/matrix-hookshot/commit/e51d8210233ac759e7f7dfebc2c4f1bf6ce94802
