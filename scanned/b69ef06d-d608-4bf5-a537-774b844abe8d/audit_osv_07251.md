# [M] Parse Server: MFA single-use token bypass via concurrent authData login requests

## Summary
Severity: Medium
Advisory: BIT-parse-2026-34224
Aliases: CVE-2026-34224, GHSA-w73w-g5xw-rwhf
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-parse-2026-34224
Type: osv

## Affected
- Bitnami: `parse` — affected >=9.0.0 <9.7.0

## Details
Parse Server is an open source backend that can be deployed to any infrastructure that can run Node.js. Prior to versions 8.6.64 and 9.7.0, an attacker who possesses a valid authentication provider token and a single MFA recovery code or SMS one-time password can create multiple authenticated sessions by sending concurrent login requests via the authData login endpoint. This defeats the single-use guarantee of MFA recovery codes and SMS one-time passwords, allowing session persistence even after the legitimate user revokes detected sessions. This issue has been patched in versions 8.6.64 and 9.7.0.

## References
- https://github.com/parse-community/parse-server/commit/661f160edac8daac0486bc94413cf9652876ab92
- https://github.com/parse-community/parse-server/commit/e7efbebba398ce6abe5b6b6fb9829c6ebe310fbf
- https://github.com/parse-community/parse-server/pull/10326
- https://github.com/parse-community/parse-server/pull/10327
- https://github.com/parse-community/parse-server/security/advisories/GHSA-w73w-g5xw-rwhf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34224
