# [M] libssh2 through 1.11.1 reads an attacker-controlled 32-bit attribute count from a...

## Summary
Severity: Medium
Advisory: JLSEC-2026-662
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-11
Source: https://osv.dev/vulnerability/JLSEC-2026-662
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.103+0

## Details
libssh2 through 1.11.1 reads an attacker-controlled 32-bit attribute count from a publickey-subsystem response and uses it in the allocation `num_attrs` * sizeof(`libssh2_publickey_attribute`) without bounds checking, so on 32-bit platforms the multiplication overflows to an undersized buffer. A malicious SSH server can then drive the attribute-parsing loop to write past the allocation, causing a heap buffer overflow in a connecting libssh2 client.

## References
- https://github.com/advisories/GHSA-mf77-5hj2-98w9
- https://github.com/bikini/exploitarium/tree/main/libssh2-publickey-list-calc-poc
- https://github.com/libssh2/libssh2/blob/master/src/publickey.c
- https://nvd.nist.gov/vuln/detail/CVE-2026-58050
- https://www.vulncheck.com/advisories/libssh2-integer-overflow-in-publickey-subsystem-attribute-allocation
