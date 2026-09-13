# [M] pimcore/admin-ui-classic-bundle Unverified Password Change

## Summary
Severity: Medium
Advisory: GHSA-6f58-j323-6472
CVE: CVE-2023-5844
CWE: CWE-287, CWE-620
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-31
Source: https://github.com/advisories/GHSA-6f58-j323-6472
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.2.0-RC1

## Details
### Impact
As old password can be set as new password , it is considered as password policy violation.

Pimcore is not enforcing strict password policy which allow attacker to set old password as new password

Proof of Concept
1. Go to Admin link
2. login and click on -> "User | My Profile".
3. Go to change password now put old password as new password and click save.

### Patches
https://github.com/pimcore/admin-ui-classic-bundle/commit/498ac77e54541177be27b0c710e387c47b3836ea.patch

### Workarounds
Update to version 1.2.0 or apply this patches manually
https://github.com/pimcore/admin-ui-classic-bundle/commit/498ac77e54541177be27b0c710e387c47b3836ea.patch

### References
https://huntr.com/bounties/b031199d-192a-46e5-8c02-f7284ad74021/

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-6f58-j323-6472
- https://nvd.nist.gov/vuln/detail/CVE-2023-5844
- https://github.com/pimcore/admin-ui-classic-bundle/commit/498ac77e54541177be27b0c710e387c47b3836ea
- https://github.com/pimcore/admin-ui-classic-bundle
- https://huntr.com/bounties/b031199d-192a-46e5-8c02-f7284ad74021
