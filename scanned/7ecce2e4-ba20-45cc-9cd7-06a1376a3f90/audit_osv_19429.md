# [M] CVE-2021-21292

## Summary
Severity: Medium
Advisory: CVE-2021-21292
Aliases: GHSA-j75r-7qm5-62q5
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N)
Published: 2021-02-02
Source: https://osv.dev/vulnerability/CVE-2021-21292
Type: osv

## Details
Traccar is an open source GPS tracking system. In Traccar before version 4.12 there is an unquoted Windows binary path vulnerability. Only Windows versions are impacted. Attacker needs write access to the filesystem on the host machine. If Java path includes a space, then attacker can lift their privilege to the same as Traccar service (system). This is fixed in version 4.12.

## References
- https://www.traccar.org/
- https://github.com/traccar/traccar/security/advisories/GHSA-j75r-7qm5-62q5
- https://github.com/traccar/traccar/commit/cc69a9907ac9878db3750aa14ffedb28626455da
