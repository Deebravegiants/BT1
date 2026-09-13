# [H] Casdoor doesn't enforce SAML assertion time bounds

## Summary
Severity: High
Advisory: GHSA-rgq2-93gj-ffxg
CVE: CVE-2026-9096
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-rgq2-93gj-ffxg
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
Casdoor versions 2.362.0 and earlier do not enforce SAML assertion time bounds. The gosaml2 library reports all time-validation results, including NotOnOrAfter and NotBefore, in the assertionInfo.WarningInfo field. However, ParseSamlResponse() never reads this field, meaning that time bounds are computed by the library but silently discarded before the user session is issued.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9096
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/780781
