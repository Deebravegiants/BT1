# [M] Entire CLI: Path traversal in checkpoint session metadata allows arbitrary file write during resume/rewind

## Summary
Severity: Medium
Advisory: GHSA-2h46-9x5w-4wf7
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:L/VA:N/SC:N/SI:H/SA:H (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-2h46-9x5w-4wf7
Type: github-advisory

## Affected
- Go: `github.com/entireio/cli` — affected >=0 <0.7.7

## Details
### Impact

A path traversal vulnerability in Entire CLI allows an attacker with push access to the checkpoints repository to craft malicious checkpoint metadata that causes `entire session resume` or `entire checkpoint rewind` to write attacker-controlled transcript data outside of the expected session directory.

The issue occurs because checkpoint metadata is fetched from the remote `entire/checkpoints/v1` branch and the `SessionID` field was used to construct filesystem paths without validation in the restore path. A malicious `SessionID` containing absolute paths or path traversal sequences could cause arbitrary files on the victim’s machine to be overwritten.

### Patches

The patched versions (`v0.7.7` or `v0.7.8-nightly.*`) observe stronger input validation and enforce traversal-resistant primitives to ensure that only descending directories can be accessed by the affected commands. 

### Workarounds
If upgrading immediately is not possible:

- Do not run `entire session resume` or `entire checkpoint rewind` on repositories where untrusted users can push to `entire/checkpoints/v1`.
- Restrict push access to shared repositories until all collaborators have upgraded.
- Inspect the `entire/checkpoints/v1` branch for suspicious checkpoint metadata before resuming or rewinding.
- Remove or protect shell initialization files and other sensitive user-writable files where feasible.

These mitigations reduce exposure but do not fully address the vulnerability. Upgrading is recommended.

### Credits
Thanks Navtej Kathuria for privately reporting this issue to the Entire Security team.

## References
- https://github.com/entireio/cli/security/advisories/GHSA-2h46-9x5w-4wf7
- https://github.com/entireio/cli/pull/1365
- https://github.com/entireio/cli/pull/1449
- https://github.com/entireio/cli
