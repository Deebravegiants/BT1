# [H] flaskBlog allows arbitrary privilege escalation

## Summary
Severity: High
Advisory: CVE-2025-55736
Aliases: GHSA-6q83-vfmq-wf72
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-55736
Type: osv

## Details
flaskBlog is a blog app built with Flask. In 2.8.0 and earlier, an arbitrary user can change his role to "admin", giving its relative privileges (e.g. delete users, posts, comments etc.). The problem is in the routes/adminPanelUsers file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55736.json
- https://github.com/DogukanUrker/FlaskBlog/security/advisories/GHSA-6q83-vfmq-wf72
- https://nvd.nist.gov/vuln/detail/CVE-2025-55736
