# [C] Signature Validation Bypass

## Summary
Severity: Critical
Advisory: GHSA-rrfw-hg9m-j47h
CWE: CWE-347
Ecosystem: Go
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-rrfw-hg9m-j47h
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/goxmldsig` — affected >=0 <0.4.2

## Details
### Impact

An authentication bypass exists in the [goxmldsig](https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-q547-gmf8-8jr7) this library uses to determine if SAML assertions are genuine. An attacker could craft a SAML response that would appear to be valid but would not have been genuinely issued by the IDP.

### Patches

Version 0.4.2 bumps the dependency which should fix the issue.

### For more information

Please see [the advisory in goxmldsig](https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-q547-gmf8-8jr7)

## Credits

The original vulnerability was discovered by @jupenur. Thanks to @russellhaering for the heads up.

## References
- https://github.com/crewjam/saml/security/advisories/GHSA-rrfw-hg9m-j47h
- https://github.com/russellhaering/goxmldsig
