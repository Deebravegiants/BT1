# [M] libssh2 through 1.11.1 grows its publickey list with `SSH2_REALLOC` but does not zero-initialize new...

## Summary
Severity: Medium
Advisory: JLSEC-2026-663
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/JLSEC-2026-663
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.103+0

## Details
libssh2 through 1.11.1 grows its publickey list with `SSH2_REALLOC` but does not zero-initialize new entries before parsing populates them, so a parse failure reaching the cleanup path leaves `libssh2_publickey_list_free` operating on an uninitialized entry. A malicious SSH server offering the publickey subsystem can use a malformed response to make cleanup free an uninitialized, attacker-influenceable attrs pointer in a connecting libssh2 client.

## References
- https://github.com/advisories/GHSA-c5f3-hwj2-xp5p
- https://github.com/bikini/exploitarium/tree/main/libssh2-publickey-list-calc-poc
- https://github.com/libssh2/libssh2/blob/master/src/publickey.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-58051
- https://www.vulncheck.com/advisories/libssh2-free-of-uninitialized-pointer-in-publickey-list-cleanup
