# [M] CVE-2026-15342

## Summary
Severity: Medium
Advisory: CVE-2026-15342
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-15342
Type: osv

## Details
Plane contains a multi‑tenant authorization flaw in its asset‑management API that allows authenticated users from one workspace to access, delete, or duplicate assets belonging to another workspace by providing only the victim workspace slug and asset ID. The affected endpoints return presigned file URLs and enable destructive or duplicative actions without verifying that the requester is a member of the targeted workspace. This enables cross‑tenant data exposure, data deletion, and persistent exfiltration of files into an attacker‑controlled workspace.

## References
- https://kb.cert.org/vuls/id/762226
- https://www.kb.cert.org/vuls/id/762226
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15342.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15342
- https://github.com/makeplane/plane
