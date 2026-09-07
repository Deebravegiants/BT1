# [C] Auth bypass in SAML provider

## Summary
Severity: Critical
Advisory: GHSA-433w-mm6h-rv9p
Ecosystem: Go
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-433w-mm6h-rv9p
Type: github-advisory

## Affected
- Go: `github.com/netlify/gotrue` — affected >=0 <1.0.0

## Details
### Impact

The following vulnerabilities have been disclosed, which impact users leveraging the SAML auth provider:

- [`goxmldsig` - Signature Validation Bypass](https://github.com/russellhaering/goxmldsig/security/advisories/GHSA-q547-gmf8-8jr7)
- [`gosaml2` - Authentication Bypass](https://github.com/russellhaering/gosaml2/security/advisories/GHSA-xhqq-x44f-9fgg)

### Patches

[Patch available](https://github.com/netlify/gotrue/pull/274)

Please upgrade to v1.0.0 or commit hash `a2b4dd6bc4ef7562d1df044098b303f564eefa90`

### Workarounds

No known workarounds.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [gotrue](https://github.com/netlify/gotrue/issues)
* Email us at [security@netlify.com](mailto:security@netlify.com)

## References
- https://github.com/netlify/gotrue/security/advisories/GHSA-433w-mm6h-rv9p
