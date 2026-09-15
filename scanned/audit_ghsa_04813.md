# [M] Nezha Monitoring: Stored future DDNS profile ID allows unauthorized use of another user's DDNS profile context

## Summary
Severity: Medium
Advisory: GHSA-39g2-8x68-pmx8
CVE: CVE-2026-53521
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-39g2-8x68-pmx8
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=2.0.14 <2.1.0

## Details
## Summary

`PATCH /server/{id}` accepts and persists nonexistent `ddns_profiles` IDs for a member-owned server. If another user later creates a DDNS profile with one of those IDs, the DDNS worker resolves the stored ID and dispatches an update using the other user's DDNS profile configuration in the context of the attacker's server.

This is a second-order authorization bypass: direct binding to an existing foreign DDNS profile is correctly denied, but an unresolved future ID can be stored first and later becomes a live cross-user reference.

## Affected versions

Confirmed on:

- Nezha `v2.0.14`
- Commit: `8b5e382fe217107c7b777ea9c6b4bc3d2e156202`

The exact affected version range was not determined.

## Impact

A normal member who owns a server can prebind one or more future DDNS profile IDs to that server. If another user later creates a DDNS profile with a matching ID, the dashboard DDNS worker can use the victim's DDNS profile/provider configuration for the attacker's server.

In the validated worker path, the dispatched DDNS update combines:

- the victim DDNS profile ID and owner
- the victim profile's provider type
- victim profile fields such as domains, access ID, access secret, and retry policy
- attacker server context, including the attacker's server ID, owner, IPv4 address, and override DDNS domains

This can result in unauthorized DDNS update attempts using another user's DDNS profile context. The attacker does not need permission to bind the victim profile after it exists.

The following were not validated: credential disclosure, account takeover, or guaranteed external DNS modification across all providers. The credentials remain server-side in the worker path. The downstream DNS impact depends on the victim profile's provider configuration and what that provider account is authorized to update.

## Affected components

- `PATCH /server/{id}`
- `cmd/dashboard/controller/server.go`
- `service/singleton/singleton.go`
- `service/singleton/ddns.go`
- `service/singleton/server.go`
- `pkg/ddns/ddns.go`

## Root cause

The server update path validates submitted DDNS profile IDs through `CheckPermission`, but that check only rejects existing objects owned by another user. Nonexistent IDs are skipped.

The `updateServer` path then persists the submitted raw IDs into `DDNSProfilesRaw`, along with override domain data. Later, the DDNS worker resolves the stored profile IDs by ID and dispatches provider updates without revalidating that the resolved profiles belong to the server owner.

As a result, an invalid unresolved reference can become a valid cross-user reference after another user creates a DDNS profile with the same global auto-increment ID.

## Reproduction summary

The behavior was validated locally with focused regression tests.

### Controller chain proof

Test file:

`cmd/dashboard/controller/ddns_second_order_test.go`

Test name:

`TestUpdateServerAllowsFutureDDNSProfileBindingThenResolvesVictimProfile`

Command:

```bash
go test ./cmd/dashboard/controller -run TestUpdateServerAllowsFutureDDNSProfileBindingThenResolvesVictimProfile -count=1
```

Result:

`pass`

The test demonstrates:

1. A normal member owns server `1`.
2. DDNS profile ID `1` does not exist.
3. The member updates their server with `enable_ddns=true` and `ddns_profiles=[1]`.
4. The request succeeds.
5. The server persists `DDNSProfiles=[1]`.
6. Another user later creates a DDNS profile and receives ID `1`.
7. A fresh attempt by the attacker to bind profile `1` is correctly denied.
8. The previously stored reference remains active and resolves in the DDNS worker path.

### Provider-level worker proof

Test file:

`service/singleton/ddns_worker_authz_test.go`

Test name:

`TestUpdateDDNSDispatchesVictimProfileForAttackerServer`

Command:

```bash
go test ./service/singleton -run TestUpdateDDNSDispatchesVictimProfileForAttackerServer -count=1
```

Result:

`pass`

The test proves that the DDNS worker does not merely resolve the victim profile. It dispatches a DDNS update using the victim profile configuration and attacker server context.

Validated assertions include:

- resolved profile ID is `1`
- resolved profile owner is victim user `200`
- processed server is attacker server `1` owned by user `100`
- provider type is the victim profile's provider
- victim profile fields are present in worker dispatch:
  - domains
  - access ID
  - access secret
  - max retries
- attacker server context is present in the same dispatch:
  - IPv4 `198.51.100.44`
- attacker-controlled override domains are passed to the worker:
  - `attacker-controlled.example`

## Practicality

The attack requires predicting or prebinding future DDNS profile IDs. This limits severity, but does not remove the authorization issue.

Evidence supporting practicality:

- DDNS profile IDs are `uint64` GORM primary keys from `model/common.go`.
- `createDDNS` uses a normal `DB.Create(&p)` flow and returns `p.ID`.
- `DDNSProfiles` is an unbounded `[]uint64` in `model/server_api.go`.
- No length or existence validation is applied in `updateServer`.
- Invalid/future IDs are preserved in the server record.
- Stored unresolved IDs survive reload.
- Range prebinding was validated with `[1,2,3,4]`.
- The DDNS worker consumes stored IDs on future DDNS update events.
- Worker dispatch can occur after server edit and agent IP-change events.
- Each DDNS update can retry according to the victim profile's `MaxRetries`.

This makes the issue semi-practical: exploitation depends on future ID prediction or range prebinding, but the unresolved IDs persist and can become active later.

## Expected behavior

`PATCH /server/{id}` should reject any submitted DDNS profile ID that does not both:

1. exist, and
2. belong to the caller or the owner of the server being updated.

The DDNS worker should also avoid trusting stored profile IDs without revalidating ownership before provider resolution or dispatch.

## Actual behavior

`PATCH /server/{id}` accepts nonexistent DDNS profile IDs and persists them. If another user later creates a DDNS profile with a matching ID, the stored reference resolves to that user's profile and is consumed by the DDNS worker for the attacker's server.

## Suggested remediation

Apply both bind-time and worker-time validation.

At bind time:

- Reject nonexistent DDNS profile IDs.
- Reject DDNS profile IDs that do not belong to the caller/server owner.
- Reject or limit excessive DDNS profile ID lists if range prebinding is not intended.

At worker time:

- Revalidate that every resolved DDNS profile still belongs to the owner of the server being processed.
- Skip or remove stale, nonexistent, or foreign DDNS profile references before provider dispatch.

Suggested regression tests:

- `TestUpdateServerRejectsNonexistentDDNSProfileIDs`
- `TestUpdateServerRejectsForeignDDNSProfileIDs`
- `TestUpdateServerAcceptsOwnedDDNSProfileIDs`
- `TestUpdateDDNSSkipsStaleOrForeignStoredDDNSProfiles`

## Security relevance

A direct bind to an existing foreign DDNS profile is already denied, which shows the intended ownership boundary. The issue is that the same boundary can be bypassed by storing a future unresolved ID before the victim profile exists.

The worker later treats the stored ID as trusted and dispatches a DDNS update using the victim profile's provider configuration with attacker server context. This is an authorization issue in a deferred worker path, not merely malformed input.

## Limitations

- The attacker does not read victim DDNS credentials through the validated path.
- Exploitation may require predicting or prebinding future global auto-increment DDNS profile IDs.
- The downstream DNS impact depends on the victim profile's provider configuration.
- External DNS modification was not claimed as guaranteed across all providers.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-39g2-8x68-pmx8
- https://nvd.nist.gov/vuln/detail/CVE-2026-53521
- https://github.com/nezhahq/nezha
