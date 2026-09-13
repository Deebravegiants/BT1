# [C] libssh2 through 1.11.1, fixed in commit 7acf3df contains an out-of-bounds write vulnerability in...

## Summary
Severity: Critical
Advisory: JLSEC-2026-661
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/JLSEC-2026-661
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.102+0

## Details
libssh2 through 1.11.1, fixed in commit 7acf3df contains an out-of-bounds write vulnerability in `ssh2_transport_read()` that fails to enforce upper bounds on `packet_length` field. Remote attackers can send crafted SSH packets with excessively large `packet_length` values to corrupt heap memory and achieve remote code execution.

## References
- https://github.com/advisories/GHSA-r8mh-x5qv-7gg2
- https://github.com/bikini/exploitarium/tree/main/libssh2-cve-2026-55200-poc
- https://github.com/libssh2/libssh2/commit/97acf3dfda80c91c3a8c9f2372546301d4a1a7a8
- https://github.com/libssh2/libssh2/pull/2052
- https://nvd.nist.gov/vuln/detail/CVE-2026-55200
- https://web.archive.org/web/20260623211210/https://github.com/bikini/exploitarium/tree/main/libssh2-cve-2026-55200-poc
- https://www.vulncheck.com/advisories/libssh2-out-of-bounds-write-via-unchecked-packet-length-in-transport-c
