# [C] Casdoor  does not validate the AudienceRestriction element in SAML assertions

## Summary
Severity: Critical
Advisory: GHSA-3w4h-g9f5-j84p
CVE: CVE-2026-9093
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-3w4h-g9f5-j84p
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
In Casdoor versions 2.362.0 and earlier, the SAML service provider implementation does not validate the AudienceRestriction element in SAML assertions. The buildSp function in object/saml_sp.go never sets AudienceURI on the gosaml2 SAMLServiceProvider struct and never inspects WarningInfo.NotInAudience. This allows assertions issued for other service providers to be accepted by Casdoor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9093
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/780781
