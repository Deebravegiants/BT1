# [M] nebula-mesh: Host revocation is not durable - blocked/offboarded hosts can regain a valid certificate

## Summary
Severity: Medium
Advisory: GHSA-339v-266x-79xr
CVE: CVE-2026-53602
CWE: CWE-613, CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-339v-266x-79xr
Type: github-advisory

## Affected
- Go: `github.com/forgekeep/nebula-mesh` — affected >=0 <0.3.7

## Details
## Summary

Two related authorization gaps let a host that should no longer be trusted obtain a fresh, valid Nebula certificate, because nebula-mgmt does not re-evaluate revocation/authorization state at certificate *issuance* time — only at poll time.

## 1. Blocklist not enforced at sign / re-enroll time

`internal/api/enroll.go:128` calls `caMgr.Sign(...)` without consulting the blocklist. The blocklist is only checked in the poll path (`internal/api/updates.go:57`, `fingerprintInBlocklist`). The blocklist is keyed by certificate *fingerprint* (`internal/store/sqlite.go`), so a re-enrollment produces a new fingerprint that is not in the blocklist.

`mintEnrollmentTokenForHost` (`internal/api/hosts.go:491`) authorizes the caller via `canAccessHost` but does **not** check the host status. There is no guard preventing a `blocked` host from transitioning back to `enrolled` (`internal/store/sqlite.go`, `enrollHostInTx` updates status unconditionally).

**Impact:** A host that an operator has blocked can be silently un-blocked by issuing a new enrollment token and re-enrolling — it receives a fresh certificate (new fingerprint) that passes all subsequent poll-time blocklist checks. Revocation is therefore not durable. Requires an operator action (minting a re-enroll token), so this is an integrity/operational-revocation failure rather than an unauthenticated bypass.

## 2. Renewal does not re-validate operator / CA status

Auto-renewal at poll time (`internal/api/updates.go:285-319`, `signHostCert`) reads `host.Name`, `host.Groups`, `host.NebulaIPs` from the DB and re-signs without checking whether the owning operator is still active or the CA still valid. `DisableOperator` (`internal/store/sqlite_operators.go`) revokes sessions and API keys but does not retire the operator's CAs, and `pki/signer.go` checks only CA cert time-expiry, not operator/CA status.

**Impact:** A host enrolled under an operator who is later disabled continues to renew its certificate indefinitely. Offboarding an operator does not cut off the hosts they provisioned.

## Affected versions

Latest tagged release (v0.3.6) and `main`.

## Remediation

1. Call a blocklist/status guard inside `handleEnroll` and `signHostCert` **before** `caMgr.Sign(...)`; refuse issuance for a host whose status is `blocked` or whose previous fingerprint is on the blocklist. Require an explicit unblock before re-enroll.
2. At renewal, re-resolve the owning operator/CA status and reject renewal if the operator is disabled or the CA retired (force re-enrollment instead).

## Discovery

Found during an internal source + offensive security audit (tracking issue #178). Adversarially cross-verified against the code paths above.

## References
- https://github.com/forgekeep/nebula-mesh/security/advisories/GHSA-339v-266x-79xr
- https://github.com/forgekeep/nebula-mesh/issues/178
- https://github.com/forgekeep/nebula-mesh
