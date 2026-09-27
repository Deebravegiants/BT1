# [M] A flaw was found in the SFTP server message decoding logic of libssh

## Summary
Severity: Medium
Advisory: JLSEC-2025-100
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-100
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0.11.0+0 <0.11.3+0

## Details
A flaw was found in the SFTP server message decoding logic of libssh. The issue occurs due to an incorrect packet length check that allows an integer overflow when handling large payload sizes on 32-bit systems. This issue leads to failed memory allocation and causes the server process to crash, resulting in a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2025-5449
- https://bugzilla.redhat.com/show_bug.cgi?id=2369705
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=261612179f740bc62ba363d98b3bd5e5573a811f
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=3443aec90188d6aab9282afc80a81df5ab72c4da
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=5504ff40515439a5fecbb17da7483000c4d12eb7
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=78485f446af9b30e37eb8f177b81940710d54496
- https://git.libssh.org/projects/libssh.git/commit/?h=stable-0.11&id=f79ec51b7fd519dbc5737a7ba826e3ed093f6ceb
- https://www.libssh.org/security/advisories/CVE-2025-5449.txt
