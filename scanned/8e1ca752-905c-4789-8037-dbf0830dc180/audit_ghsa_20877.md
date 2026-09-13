# [H] Dendrite signature checks not applied to some retrieved missing events

## Summary
Severity: High
Advisory: GHSA-pfw4-xjgm-267c
CVE: CVE-2022-39200
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-pfw4-xjgm-267c
Type: github-advisory

## Affected
- Go: `github.com/matrix-org/dendrite` — affected >=0 <0.9.8

## Details
### Impact

Events retrieved from a remote homeserver using `/get_missing_events` did not have their signatures verified correctly. This could potentially allow a remote homeserver to provide invalid/modified events to Dendrite via this endpoint.

Note that this does not apply to events retrieved through other endpoints (e.g. `/event`, `/state`) as they have been correctly verified.

Homeservers that have federation disabled are not vulnerable.

### Patches

The problem has been fixed in Dendrite 0.9.8.

### Workarounds

There are no workarounds.

### Special thanks

Tulir Asokan, who spotted the issue originally.

## References
- https://github.com/matrix-org/dendrite/security/advisories/GHSA-pfw4-xjgm-267c
- https://nvd.nist.gov/vuln/detail/CVE-2022-39200
- https://github.com/matrix-org/dendrite/commit/2792d0490f3771488bad346981b8c26479a872c3
- https://github.com/matrix-org/dendrite
