# [H] Plainpad: Privilege Escalation via Writable Admin Field in Profile Update (Access Control)

## Summary
Severity: High
Advisory: CVE-2026-42562
Aliases: GHSA-pvfv-wvpm-q6f6
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-05-09
Source: https://osv.dev/vulnerability/CVE-2026-42562
Type: osv

## Details
Plainpad is a self hosted note taking app. Prior to version 1.1.1, Plainpad allows a low-privilege authenticated user to self-escalate to administrator by submitting admin=true in PUT /api.php/v1/users/{id}. The endpoint directly persists the admin attribute from user input, and the escalated account can immediately access admin-only routes. This issue has been patched in version 1.1.1.

## References
- https://github.com/alextselegidis/plainpad/releases/tag/1.1.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42562.json
- https://github.com/alextselegidis/plainpad/security/advisories/GHSA-pvfv-wvpm-q6f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-42562
- https://github.com/alextselegidis/plainpad/issues/138
- https://github.com/alextselegidis/plainpad/commit/9216a876d27b22c3d9259551636d803f7cb075fc
