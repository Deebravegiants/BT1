# [H] Improper Neutralization of Special Elements used in an LDAP Query in stevenweathers/thunderdome-planning-poker

## Summary
Severity: High
Advisory: GHSA-26cm-qrc6-mfgj
CVE: CVE-2021-41232
CWE: CWE-116, CWE-74, CWE-90
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-26cm-qrc6-mfgj
Type: github-advisory

## Affected
- Go: `github.com/stevenweathers/thunderdome-planning-poker` — affected >=0 <1.16.3

## Details
### Impact
LDAP injection vulnerability, only affects instances with LDAP authentication enabled.

### Patches
Patch for vulnerability released with v1.16.3.

### Workarounds
Disable LDAP feature if in use

### References
[OWASP LDAP Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LDAP_Injection_Prevention_Cheat_Sheet.html
)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Thunderdome Github Repository](https://github.com/StevenWeathers/thunderdome-planning-poker)
* Email us at [steven@weathers.me](mailto:steven@weathers.me)

## References
- https://github.com/StevenWeathers/thunderdome-planning-poker/security/advisories/GHSA-26cm-qrc6-mfgj
- https://nvd.nist.gov/vuln/detail/CVE-2021-41232
- https://github.com/github/securitylab/issues/464#issuecomment-957094994
- https://github.com/StevenWeathers/thunderdome-planning-poker/commit/f1524d01e8a0f2d6c3db5461c742456c692dd8c1
- https://github.com/StevenWeathers/thunderdome-planning-poker
