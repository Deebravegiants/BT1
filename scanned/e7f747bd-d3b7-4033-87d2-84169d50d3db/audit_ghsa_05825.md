# [M] New API: Admin can reset passkeys for same-level or higher-privileged users

## Summary
Severity: Medium
Advisory: GHSA-p845-629j-rcj6
CVE: CVE-2026-64866
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-p845-629j-rcj6
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0.9.1.3 <1.0.0-rc.7

## Details
## Summary

The admin passkey reset endpoint lacked the role-level authorization check used by comparable privileged account-protection endpoints. A lower-privileged administrator could attempt passkey reset operations against same-level or higher-privileged users, including root-level accounts.

## Impact

If the target account had a passkey configured, a lower-privileged administrator could remove that authentication factor and weaken the target account's protection boundary. The attacker still needed administrator privileges, so the issue is rated Medium.

## Affected versions

The vulnerable admin passkey reset behavior was present from the passkey feature introduction in `v0.9.1.3` through versions before `v1.0.0-rc.7`.

## Patches

This issue is fixed in `v1.0.0-rc.7`. The fix adds a `canManageTargetRole` check to `AdminResetPasskey` before passkey lookup or deletion, preventing lower-privileged administrators from operating on same-level or higher-privileged users.

## Workarounds

If upgrading immediately is not possible, restrict admin access to trusted operators only and block `DELETE /api/user/:id/reset_passkey` at the reverse proxy or gateway except for root operators.

## References

- Fixed by commit `0936e2504655a5cbf7bc3c388f6d3e2bb24916d3`.
- Relevant code paths: `controller/passkey.go`, `controller/twofa.go`, and `router/api-router.go`.

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-p845-629j-rcj6
- https://github.com/QuantumNous/new-api/pull/4929
- https://github.com/QuantumNous/new-api/commit/0936e2504655a5cbf7bc3c388f6d3e2bb24916d3
- https://github.com/QuantumNous/new-api
- https://github.com/QuantumNous/new-api/releases/tag/v1.0.0-rc.7
