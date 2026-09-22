# [M] A flaw was found in libssh, a library that implements the SSH protocol

## Summary
Severity: Medium
Advisory: JLSEC-2025-99
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-99
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.11.3+0

## Details
A flaw was found in libssh, a library that implements the SSH protocol. When calculating the session ID during the key exchange (KEX) process, an allocation failure in cryptographic functions may lead to a NULL pointer dereference. This issue can cause the client or server to crash.

## References
- https://access.redhat.com/errata/RHSA-2026:18683
- https://access.redhat.com/security/cve/CVE-2025-8114
- https://bugzilla.redhat.com/show_bug.cgi?id=2383220
- https://git.libssh.org/projects/libssh.git/commit/?id=53ac23ded4cb2c5463f6c4cd1525331bd578812d
- https://git.libssh.org/projects/libssh.git/commit/?id=65f363c9
- https://www.libssh.org/security/advisories/CVE-2025-8114.txt
