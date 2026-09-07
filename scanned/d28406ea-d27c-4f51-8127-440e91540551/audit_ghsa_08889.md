# [M] ots has a negative expire override that can bypass its secret retention policy

## Summary
Severity: Medium
Advisory: GHSA-h5fq-653g-gxrm
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-h5fq-653g-gxrm
Type: github-advisory

## Affected
- Go: `github.com/Luzifer/ots` — affected >=0 <1.21.5

## Details
## Summary

The `/api/create` endpoint accepted negative `expire` query values. For the memory storage backend, negative values were passed to secret creation as a negative duration and treated as no expiry, allowing callers to create secrets that persisted longer than intended.

## Impact

Unauthenticated users could bypass configured retention expectations for secrets they create by sending `POST /api/create?expire=-1`.

This does not allow reading or modifying secrets created by other users. Secrets remain one-time-read and, in the normal web flow, client-side encrypted.

## Affected versions

Versions up to and including v1.21.4 are affected.

## Patched versions

Fixed in v1.21.5.

## Workarounds

Disable expiry overrides via `disableExpiryOverride: true` until upgrading.

## Credit

Reported by Chai Cheng Xun via email.

## References
- https://github.com/Luzifer/ots/security/advisories/GHSA-h5fq-653g-gxrm
- https://github.com/Luzifer/ots/commit/3511bd18a2bec75bd9c6b4d513f2a90ccf4209b7
- https://github.com/Luzifer/ots
- https://github.com/Luzifer/ots/releases/tag/v1.21.5
