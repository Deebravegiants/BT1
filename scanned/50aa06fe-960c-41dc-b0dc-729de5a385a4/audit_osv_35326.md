# [M] Authorization Bypass due to Incorrect Access Control in danny-avila/librechat

## Summary
Severity: Medium
Advisory: CVE-2025-7106
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-7106
Type: osv

## Details
danny-avila/librechat is affected by an authorization bypass vulnerability due to improper access control checks. The `checkAccess` function in `api/server/middleware/roles/access.js` uses `permissions.some()` to validate permissions, which incorrectly grants access if only one of multiple required permissions is present. This allows users with the 'USER' role to create agents despite having `CREATE: false` permission, as the check for `['USE', 'CREATE']` passes with just `USE: true`. This vulnerability affects other permission checks as well, such as `PROMPTS`. The issue is present in all versions prior to the fix.

## References
- https://huntr.com/bounties/7de2765b-d1fe-4495-9144-220070857c48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7106.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7106
- https://github.com/danny-avila/librechat/commit/91a2df47599c09d80886bfc28e0ccf1debd42110
