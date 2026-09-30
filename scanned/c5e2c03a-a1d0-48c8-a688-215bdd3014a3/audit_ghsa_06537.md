# [M] @backstage/plugin-auth-backend: Unauthenticated OAuth account takeover via `redirect_uri` allowlist bypass

## Summary
Severity: Medium
Advisory: GHSA-38hq-7x33-php4
CVE: CVE-2026-73563
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-38hq-7x33-php4
Type: github-advisory

## Affected
- npm: `@backstage/plugin-auth-backend` — affected >=0 <0.29.2

## Details
### Impact
The allowlist matching used by the experimental dynamic client registration and client ID metadata document (CIMD) features in `@backstage/plugin-auth-backend` matched glob patterns against the full URL string. A * wildcard could therefore match across URL component boundaries: a pattern such as `https://*.example.com/callback`, intended to allow subdomains of a trusted host, would also match an attacker-controlled URL such as `https://attacker.example/x.example.com/callback`. This applies to `auth.experimentalDynamicClientRegistration.allowedRedirectUriPatterns` as well as the `allowedClientIdPatterns` and `allowedRedirectUriPatterns` options of `auth.experimentalClientIdMetadataDocuments`.

An attacker could use this to register an OAuth client whose redirect URI points to a host they control while still passing the allowlist, causing authorization codes to be delivered to the attacker when a victim completes an authorization flow. In addition, allowlist patterns without an explicit protocol could match URLs with any protocol, and redirect URIs containing embedded credentials (user:pass@host) were accepted after the credentials were stripped for matching.

The practical impact is limited. Both features are experimental and disabled by default, and the default allowlist patterns only reference fixed or loopback hosts and are not affected. Deployments are only impacted if they enable one of these features and configure custom allowlist patterns that contain a wildcard in the hostname, or patterns without an explicit protocol.

### Patches
Patched in `@backstage/plugin-auth-backend` version `0.29.2`. Patterns are now matched against each URL component separately so that wildcards no longer match across the host and path boundary, patterns without an explicit protocol are rejected as invalid configuration, and redirect URIs with embedded credentials are always rejected.

Note that as part of this fix, a wildcard port no longer implicitly matches every path: a pattern such as `http://localhost:*` now only matches the root path. Use `http://localhost:*/*` to allow any port and any path.

### Workarounds
Disable the experimental features by removing `auth.experimentalDynamicClientRegistration` and `auth.experimentalClientIdMetadataDocuments` from your `app-config`, which is the default configuration. Alternatively, restrict the configured allowlist patterns to fully specified URLs with an explicit protocol and no wildcard in the hostname, which are not affected by this vulnerability.

## References
- https://github.com/backstage/backstage/security/advisories/GHSA-38hq-7x33-php4
- https://github.com/backstage/backstage/commit/274acc51d22a7dd919cdda49d9086cf12c0b8711
- https://github.com/backstage/backstage/commit/6370e53bce8b227c63092300594ffde29c006886
- https://github.com/backstage/backstage/commit/ef606a85545cb6d765e20afd1ff43ae5407a3660
- https://github.com/backstage/backstage/commit/fdc0d2dcd9a571e3839d7f5de4133c4e242a3a41
- https://github.com/backstage/backstage
- https://github.com/backstage/backstage/releases/tag/v1.53.0
