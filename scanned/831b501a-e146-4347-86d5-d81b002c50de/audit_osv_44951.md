# [H] passport-saml-encrypted through 0.1.13 XML Signature Wrapping via Assertion Prepending

## Summary
Severity: High
Advisory: CVE-2026-89043
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-89043
Type: osv

## Details
passport-saml-encrypted through 0.1.13 contains an XML signature wrapping vulnerability where signature verification and assertion extraction use independent XPath lookups with no cross-validation. Attackers holding any validly signed SAML message can prepend a forged unsigned assertion that gets accepted as the verified identity while the genuine signature validates against the original assertion.

## References
- https://www.npmjs.com/package/passport-saml-encrypted
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89043.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-89043
- https://www.vulncheck.com/advisories/passport-saml-encrypted-through-0.1.13-xml-signature-wrapping-via-assertion-prepending
- https://github.com/krakenjs/passport-saml-encrypted/issues/30
- https://github.com/krakenjs/passport-saml-encrypted
- https://github.com/krakenjs/passport-saml-encrypted/blob/v0.1.13/lib/saml.js#L256
- https://github.com/krakenjs/passport-saml-encrypted/blob/v0.1.13/lib/saml.js#L328
