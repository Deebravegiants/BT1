# [C] Critical security issues in XML encoding in github.com/dexidp/dex

## Summary
Severity: Critical
Advisory: GHSA-m9hp-7r99-94h5
CVE: CVE-2020-26290
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-m9hp-7r99-94h5
Type: github-advisory

## Affected
- Go: `github.com/dexidp/dex` — affected >=0 <2.27.0
- Go: `github.com/russellhaering/goxmldsig` — affected >=0 <1.1.0

## Details
### Impact

The following vulnerabilities have been disclosed, which impact users leveraging the SAML connector:

Signature Validation Bypass (CVE-2020-15216): https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-q547-gmf8-8jr7

`encoding/xml` instabilities:
 - [Element namespace prefix instability (CVE-2020-29511)](https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-elements.md)
 - [Attribute namespace prefix instability (CVE-2020-29509)](https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-attributes.md)
 - [Directive comment instability (CVE-2020-29510)](https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-directives.md)

### Patches

Immediately update to [Dex v2.27.0](https://github.com/dexidp/dex/releases/tag/v2.27.0).

### Workarounds

There are no known workarounds.

## References
- https://github.com/dexidp/dex/security/advisories/GHSA-m9hp-7r99-94h5
- https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-q547-gmf8-8jr7
- https://nvd.nist.gov/vuln/detail/CVE-2020-26290
- https://github.com/dexidp/dex/commit/324b1c886b407594196113a3dbddebe38eecd4e8
- https://github.com/russellhaering/goxmldsig/commit/f6188febf0c29d7ffe26a0436212b19cb9615e64
- https://github.com/dexidp/dex/releases/tag/v2.27.0
- https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-attributes.md
- https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-directives.md
- https://github.com/mattermost/xml-roundtrip-validator/blob/master/advisories/unstable-elements.md
- https://mattermost.com/blog/coordinated-disclosure-go-xml-vulnerabilities
- https://pkg.go.dev/vuln/GO-2020-0050
