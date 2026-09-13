# [H] WireGuard Portal v2 Vulnerable to OAuth Insecure Redirect URI / Account Takeover

## Summary
Severity: High
Advisory: GHSA-2r2v-9pf8-6342
Ecosystem: Go
Published: 2025-01-07
Source: https://github.com/advisories/GHSA-2r2v-9pf8-6342
Type: github-advisory

## Affected
- Go: `github.com/h44z/wg-portal` — affected >=2.0.0-alpha.1 <2.0.0-alpha.3

## Details
### Impact
Users of WireGuard Portal v2 who have OAuth (or OIDC) authentication backends enabled can be affected by an Account Takeover vulnerability if they visit a malicious website.

### Patches
The problem was fixed in the latest alpha release, v2.0.0-alpha.3. The [docker images](https://hub.docker.com/r/wgportal/wg-portal) for the tag 'latest' built from the master branch also include the fix.

## References
- https://github.com/h44z/wg-portal/security/advisories/GHSA-2r2v-9pf8-6342
- https://github.com/h44z/wg-portal/commit/62dbdfe0f96045d46e121d509fc181fbb7936895
- https://github.com/h44z/wg-portal
