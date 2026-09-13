# [H] passport-saml-encrypted through 0.1.13 Authentication Bypass via Missing Signature Verification

## Summary
Severity: High
Advisory: CVE-2026-89042
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-89042
Type: osv

## Details
passport-saml-encrypted through 0.1.13 makes SAML signature verification conditional on an optional cert option, allowing attackers to bypass authentication by submitting unsigned SAML responses. Attackers can post forged SAML responses with arbitrary NameID and attributes to the assertion consumer service endpoint to receive authenticated profiles without valid signatures.

## References
- https://www.npmjs.com/package/passport-saml-encrypted
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/89xxx/CVE-2026-89042.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-89042
- https://www.vulncheck.com/advisories/passport-saml-encrypted-through-0.1.13-authentication-bypass-via-missing-signature-verification
- https://github.com/krakenjs/passport-saml-encrypted/issues/29
- https://github.com/krakenjs/passport-saml-encrypted
- https://github.com/krakenjs/passport-saml-encrypted/blob/v0.1.13/lib/saml.js#L296
- https://github.com/krakenjs/passport-saml-encrypted/blob/v0.1.13/lib/saml.js#L321
