# [M] OpenBao's Kerberos Auth Method Accumulates Unaccessible Tokens

## Summary
Severity: Medium
Advisory: GHSA-7j6w-vvw2-5f9c
CVE: CVE-2026-46405
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-7j6w-vvw2-5f9c
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <2.5.4

## Details
### Impact

In OpenBao's Kerberos auth method on the `GET` handler, or when an `Authorization: Negotiate` header is supplied, the response is includes a `logical.Auth` object in addition to an error message. This results in tokens being created with only the default policy, default TTL, and no entity information, which are hidden by the returned error message. No access to these tokens by the caller occurs and the authentication token is not ever made accessible outside of `sys/raw`. At most this could cause storage usage.

### Patches

This is fixed in OpenBao v2.5.4. 

### Workarounds

Users may set a rate limit quota to limit the creation of these paths. As the path is unauthenticated, it isn't possible to deny access to it.

### Reporter

This was discovered by an anonymous reporter.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-7j6w-vvw2-5f9c
- https://github.com/openbao/openbao/pull/3150
- https://github.com/openbao/openbao/commit/0d82e0a5a3b6a93e8087bcbaf0b11326c12d4f4d
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.5.4
