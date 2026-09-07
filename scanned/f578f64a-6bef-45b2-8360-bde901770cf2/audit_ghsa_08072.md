# [H] Formwork Improperly Managed Privileges in User creation

## Summary
Severity: High
Advisory: GHSA-34p4-7w83-35g2
CVE: CVE-2026-27198
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-34p4-7w83-35g2
Type: github-advisory

## Affected
- Packagist: `getformwork/formwork` — affected >=2.0.0 <2.3.4

## Details
### Summary

The application fails to properly enforce role-based authorization during account creation. Although the system validates that the specified role exists, it does not verify whether the current user has sufficient privileges to assign highly privileged roles such as admin. As a result, an authenticated user with the editor role can create a new account with administrative privileges, leading to full administrative access and complete compromise of the CMS.

### Impact

Successful exploitation allows an attacker to:
- Gain full administrative control over the CMS.
- Access all site data and user information.  
- Modify system configuration and security settings.
- Create, modify, or delete any user account, including legitimate administrators.

### Patches

[Formwork 2.3.4](https://github.com/getformwork/formwork/releases/tag/2.3.4)  properly assigns roles on user creation.

## References
- https://github.com/getformwork/formwork/security/advisories/GHSA-34p4-7w83-35g2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27198
- https://github.com/getformwork/formwork/commit/19390a0b408e084bdef86f3581e050f3ee51e7cd
- https://github.com/getformwork/formwork
- https://github.com/getformwork/formwork/releases/tag/2.3.4
