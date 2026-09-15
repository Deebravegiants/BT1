# [M] Improper Authentication in CraftCMS two factor authentication plugin

## Summary
Severity: Medium
Advisory: GHSA-96qm-hwhp-2rm8
CVE: CVE-2024-5658
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-96qm-hwhp-2rm8
Type: github-advisory

## Affected
- Packagist: `born05/craft-twofactorauthentication` — affected >=0 <3.3.4

## Details
The CraftCMS plugin Two-Factor Authentication through 3.3.3 allows reuse of TOTP tokens multiple times within the validity period.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5658
- https://github.com/born05/craft-twofactorauthentication/commit/89d2339463c0f3ee690e707d4bc8501360885289
- https://github.com/born05/craft-twofactorauthentication
- https://github.com/born05/craft-twofactorauthentication/releases/tag/3.3.4
- https://github.com/sbaresearch/advisories/tree/public/2024/SBA-ADV-20240202-02_CraftCMS_Plugin_Two-Factor_Authentication_TOTP_Valid_After_Use
- https://plugins.craftcms.com/two-factor-authentication?craft4
- http://www.openwall.com/lists/oss-security/2024/06/06/2
