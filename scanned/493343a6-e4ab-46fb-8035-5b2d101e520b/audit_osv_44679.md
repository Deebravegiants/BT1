# [M] MOOS core-moos through 10.4.0 Remote Process Termination via Hard-Coded Multicast Passphrase

## Summary
Severity: Medium
Advisory: CVE-2026-85451
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85451
Type: osv

## Details
MOOS core-moos through 10.4.0 contains a remote process termination vulnerability in the SuicidalSleeper component that uses a hard-coded passphrase for multicast command authorization. Any multicast-reachable peer can enumerate MOOS processes and send termination commands to trigger process shutdown by exploiting the default multicast group and port with the known passphrase.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85451.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85451
- https://www.vulncheck.com/advisories/moos-core-moos-through-10.4.0-remote-process-termination-via-hard-coded-multicast-passphrase
- https://github.com/themoos/core-moos/commit/488806a07db9f21eea124f48a9c0392f058f01dc
- https://github.com/themoos/core-moos/pull/85
- https://github.com/themoos/core-moos
- https://github.com/themoos/core-moos/blob/ec9c77c68fcbdef8f5e4c60fe243acd223433f0c/Core/libMOOS/Comms/SuicidalSleeper.cpp#L45
