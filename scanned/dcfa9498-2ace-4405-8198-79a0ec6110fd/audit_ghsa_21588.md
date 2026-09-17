# [C] crewjam/saml vulnerable to signature bypass via multiple Assertion elements due to improper authentication

## Summary
Severity: Critical
Advisory: GHSA-j2jp-wvqg-wc2g
CVE: CVE-2022-41912
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-11-29
Source: https://github.com/advisories/GHSA-j2jp-wvqg-wc2g
Type: github-advisory

## Affected
- Go: `github.com/crewjam/saml` — affected >=0 <0.4.9

## Details
### Impact

The crewjam/saml go library is vulnerable to an authentication bypass when processing SAML responses containing multiple Assertion elements.

### Patches

This issue has been corrected in version 0.4.9.

### Credit

This issue was reported by Felix Wilhelm from Google Project Zero.

## References
- https://github.com/crewjam/saml/security/advisories/GHSA-j2jp-wvqg-wc2g
- https://github.com/prometheus/exporter-toolkit/security/advisories/GHSA-7rg2-cxvp-9p7p
- https://nvd.nist.gov/vuln/detail/CVE-2022-41912
- https://github.com/crewjam/saml/commit/aee3fb1edeeaf1088fcb458727e0fd863d277f8b
- https://github.com/crewjam/saml
- https://github.com/crewjam/saml/releases/tag/v0.4.9
- https://pkg.go.dev/vuln/GO-2022-1129
- http://packetstormsecurity.com/files/170356/crewjam-saml-Signature-Bypass.html
