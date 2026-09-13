# [H] Open eClass Insecure Password Reset Token Reuse Enables Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-24669
Aliases: GHSA-gcqq-fxw6-f866
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-24669
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, an insecure password reset mechanism allows local attackers to reuse a valid password reset token after it has already been used, enabling unauthorized password changes and potential account takeover. This issue has been patched in version 4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24669.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-gcqq-fxw6-f866
- https://nvd.nist.gov/vuln/detail/CVE-2026-24669
