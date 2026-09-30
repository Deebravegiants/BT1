# [M] ALPINE-CVE-2022-46176

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-46176
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-01-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-46176
Type: osv

## Affected
- Alpine:v3.19: `rust` — affected >=0 <1.66.1-r0
- Alpine:v3.20: `rust` — affected >=0 <1.66.1-r0
- Alpine:v3.21: `rust` — affected >=0 <1.66.1-r0
- Alpine:v3.22: `rust` — affected >=0 <1.66.1-r0
- Alpine:v3.23: `rust` — affected >=0 <1.66.1-r0
- Alpine:v3.24: `rust` — affected >=0 <1.66.1-r0

## Details
Cargo is a Rust package manager. The Rust Security Response WG was notified that Cargo did not perform SSH host key verification when cloning indexes and dependencies via SSH. An attacker could exploit this to perform man-in-the-middle (MITM) attacks. This vulnerability has been assigned CVE-2022-46176. All Rust versions containing Cargo before 1.66.1 are vulnerable. Note that even if you don't explicitly use SSH for alternate registry indexes or crate dependencies, you might be affected by this vulnerability if you have configured git to replace HTTPS connections to GitHub with SSH (through git's [`url.<base>.insteadOf`][1] setting), as that'd cause you to clone the crates.io index through SSH. Rust 1.66.1 will ensure Cargo checks the SSH host key and abort the connection if the server's public key is not already trusted. We recommend everyone to upgrade as soon as possible.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-46176
