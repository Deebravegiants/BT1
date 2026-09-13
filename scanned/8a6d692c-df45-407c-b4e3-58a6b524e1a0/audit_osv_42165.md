# [H] CVE-2026-64773

## Summary
Severity: High
Advisory: CVE-2026-64773
Aliases: GHSA-wg28-286f-56v6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-64773
Type: osv

## Details
An attacker that can reach a container's published TCP port may be able to force the host's forwarding process to buffer an unbounded amount of that client's data in memory, for as long as the backend container connection takes to complete — with no cap on how much accumulates or how long the wait can be stretched. This vulnerability is addressed in container version 1.2.0.

## References
- https://github.com/apple/container/security/advisories/GHSA-wg28-286f-56v6
