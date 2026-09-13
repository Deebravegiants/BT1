# [H] ViewVC's standalone server exposes arbitrary server filesystem content

## Summary
Severity: High
Advisory: CVE-2025-54141
Aliases: GHSA-rv3m-76rj-q397
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-54141
Type: osv

## Details
ViewVC is a browser interface for CVS and Subversion version control repositories. In versions 1.1.0 through 1.1.31 and 1.2.0 through 1.2.3, the standalone.py script provided in the ViewVC distribution can expose the contents of the host server's filesystem though a directory traversal-style attack. This is fixed in versions 1.1.31 and  1.2.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54141.json
- https://github.com/viewvc/viewvc/security/advisories/GHSA-rv3m-76rj-q397
- https://nvd.nist.gov/vuln/detail/CVE-2025-54141
- https://github.com/viewvc/viewvc/issues/211
- https://github.com/viewvc/viewvc/commit/1dd84542c39b39e4a3f434db84a8ba3441d6a1e7
- https://github.com/viewvc/viewvc/commit/5d7c76be07b77dce4ff631e9b866056344f11e84
