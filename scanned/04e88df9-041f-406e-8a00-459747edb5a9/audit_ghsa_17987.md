# [M] Contao applies improper access control in the back end voters

## Summary
Severity: Medium
Advisory: GHSA-7m47-r75r-cx8v
CVE: CVE-2025-57758
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-7m47-r75r-cx8v
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=5.0.0 <5.3.38
- Packagist: `contao/core-bundle` — affected >=5.4.0-RC1 <5.6.1
- Packagist: `contao/contao` — affected >=5.0.0 <5.3.38
- Packagist: `contao/contao` — affected >=5.4.0-RC1 <5.6.1

## Details
### Impact

The table access voter in the back end doesn't check if a user is allowed to access the corresponding module.

### Patches

Update to Contao 5.3.38 or 5.6.1.

### Workarounds

Do not rely solely on the voter and additionally check `USER_CAN_ACCESS_MODULE`.

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-7m47-r75r-cx8v
- https://nvd.nist.gov/vuln/detail/CVE-2025-57758
- https://github.com/contao/contao/commit/3f05c603e1c94d34819f837f060df5d66447d0d7
- https://contao.org/en/security-advisories/improper-access-control-in-the-back-end-voters
- https://github.com/contao/contao
