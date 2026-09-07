# [M] New API has passkey-based secure step-up verification bypass for root-only channel secret disclosure

## Summary
Severity: Medium
Advisory: GHSA-5353-f8fq-65vc
CVE: CVE-2026-32879
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-5353-f8fq-65vc
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0.10.0

## Details
## Summary

A logic flaw in the universal secure verification flow allows an authenticated user with a registered passkey to satisfy secure verification without completing a WebAuthn assertion.

## Affected versions

>= v0.10.0

## Description

The `POST /api/verify` endpoint supports multiple secure verification methods, including passkeys. When the request body contains `{"method":"passkey"}`, the server only checks whether the authenticated account has a passkey record on file and then marks the secure verification session as complete. It does not verify that the requester successfully completed a WebAuthn assertion.

As a result, an authenticated user who already has a valid session and a registered passkey can satisfy the secure verification requirement without performing the intended passkey challenge/response flow.

## Impact

In the upstream project, this issue affects actions protected by `SecureVerificationRequired()`. At the time of publication, the confirmed upstream impact is the root-only `POST /api/channel/:id/key` endpoint, which returns stored channel secrets.

Successful exploitation requires:
- an already authenticated session for the target account, and
- a registered passkey on that account.

No full login bypass or cross-account privilege escalation has been confirmed in the upstream codebase. However, the issue defeats the intended step-up verification control for affected privileged actions.

## Workarounds

Until a patched release is applied:
- do not rely on passkey as the step-up method for privileged secure-verification actions;
- require TOTP/2FA for those actions where operationally possible; or
- temporarily restrict access to affected secure-verification-protected endpoints.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-5353-f8fq-65vc
- https://github.com/QuantumNous/new-api
