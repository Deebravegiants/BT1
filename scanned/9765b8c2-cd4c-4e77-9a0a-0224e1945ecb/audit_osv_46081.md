# [M] libssh2 through 1.11.1, fixed in commit 1762685, contains a pre-authentication denial of service...

## Summary
Severity: Medium
Advisory: JLSEC-2026-660
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/JLSEC-2026-660
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.102+0

## Details
libssh2 through 1.11.1, fixed in commit 1762685, contains a pre-authentication denial of service vulnerability in the `SSH_MSG_EXT_INFO` handler in `src/packet.c` that allows a malicious SSH server to cause a client CPU exhaustion loop by sending a crafted extension count value. A malicious server can set `nr_extensions` to 0xFFFFFFFF during key exchange, causing the client to spin in a tight CPU loop for over 60 seconds because return values from `_libssh2_get_string()` are unchecked and the session timeout does not apply to CPU-bound loops.

## References
- https://github.com/advisories/GHSA-3cfq-4xx4-rmpg
- https://github.com/libssh2/libssh2/commit/17626857d20b3c9a1addfa45979dadcee1cd84a4
- https://github.com/libssh2/libssh2/pull/1864
- https://nvd.nist.gov/vuln/detail/CVE-2026-55199
- https://www.vulncheck.com/advisories/libssh2-pre-authentication-dos-via-ssh-msg-ext-info-handler
