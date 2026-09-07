# [H] Cross-site Scripting via missing Binding syntax validation

## Summary
Severity: High
Advisory: GHSA-267v-3v32-g6q5
CVE: CVE-2023-45683
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-267v-3v32-g6q5
Type: github-advisory

## Affected
- Go: `github.com/crewjam/saml` — affected >=0 <0.4.14

## Details
### Impact

The package does not validate the ACS Location URI according to the SAML binding being parsed.

If abused, this flaw allows attackers to register malicious Service Providers at the IdP and inject Javascript in the ACS endpoint definition, achieving Cross-Site-Scripting (XSS) in the IdP context during the redirection at the end of a SAML SSO Flow.

Consequently, an attacker may perform any authenticated action as the victim once the victim’s browser loaded the SAML IdP initiated SSO link for the malicious service provider.

Note: The severity is considered “High” because the SP registration is commonly an unrestricted operation in IdPs, hence not requiring particular permissions or publicly accessible to ease the IdP interoperability.

### Patches

This issue is fixed in 0.4.14

### Workarounds

Users of the package can perform external validation of URLs provided in SAML metadata, or restrict the ability for end-users to upload arbitrary metadata. 

### References

This issue was reported by Francesco Lacerenza from Doyensec.

## References
- https://github.com/crewjam/saml/security/advisories/GHSA-267v-3v32-g6q5
- https://nvd.nist.gov/vuln/detail/CVE-2023-45683
- https://github.com/crewjam/saml/commit/b07b16cf83c4171d16da4d85608cb827f183cd79
- https://github.com/crewjam/saml
