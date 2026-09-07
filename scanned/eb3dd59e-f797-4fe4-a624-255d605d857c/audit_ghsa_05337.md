# [H] Blnk has an API key authorization bypass in owner and scope enforcement

## Summary
Severity: High
Advisory: GHSA-wcr3-9x4c-f5gj
CWE: CWE-863
Ecosystem: Go
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-wcr3-9x4c-f5gj
Type: github-advisory

## Affected
- Go: `github.com/blnkfinance/blnk` — affected >=0 <0.14.3

## Details
Blnk API key endpoints had an authorization issue that allowed non-master API keys to perform key-management actions outside their intended authorization boundary.

In affected versions, API key operations trusted caller-controlled request values for owner and scope decisions. As a result, a non-master API key could potentially manage keys for another owner by supplying a different owner value, or create a more privileged API key by requesting broader scopes than it already had.

This has been fixed by deriving the effective owner from the authenticated API key and enforcing scope coverage checks when creating new keys.

## Details

The API key authorization flow previously trusted request data supplied by the caller when deciding which owner a key-management operation applied to and which scopes could be granted.

This meant a non-master API key could potentially:

- create API keys for another owner
- list API keys belonging to another owner
- revoke API keys belonging to another owner
- create a new API key with broader scopes than the caller’s own scopes

The patched version changes this behavior for non-master API keys:

- the effective owner is derived from the authenticated API key
- caller-supplied owner values are no longer trusted for authorization decisions
- cross-owner key operations are rejected with `403 Forbidden`
- requested scopes must be covered by the caller’s existing scopes
- master-key behavior is unchanged

## Impact

A non-master API key with access to API key management endpoints could potentially perform unauthorized key-management operations across owners or escalate its permissions by creating a new API key with broader scopes.

Deployments using API keys for programmatic key creation, listing, or revocation should upgrade.

## Affected versions

Versions up to and including `v0.14.2` are affected.

## Patched versions

This issue is fixed in `v0.14.3`.

Users should upgrade to `v0.14.3` or later.

## Workarounds

If developers cannot upgrade their applications immediately, restrict access to API key management endpoints to trusted master keys only.

Where possible, disable or block non-master API key access to key creation, listing, and revocation endpoints until the patched version is deployed.

## Credits

Blank thanks @Shivam8584 for identifying and fixing this issue.

## References
- https://github.com/blnkfinance/blnk/security/advisories/GHSA-wcr3-9x4c-f5gj
- https://github.com/blnkfinance/blnk
