# [H] JLSEC-2026-784

## Summary
Severity: High
Advisory: JLSEC-2026-784
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/JLSEC-2026-784
Type: osv

## Affected
- Julia: `libssh_jll` — affected >=0 <0.11.4+0

## Details
A weakness has been identified in libssh up to 0.11.3. The impacted element is the function `sftp_extensions_get_name/sftp_extensions_get_data` of the file `src/sftp.c` of the component SFTP Extension Name Handler. Executing a manipulation of the argument idx can lead to out-of-bounds read. The attack may be performed from remote. Upgrading to version 0.11.4 and 0.12.0 is sufficient to resolve this issue. This patch is called 855a0853ad3abd4a6cd85ce06fce6d8d4c7a0b60. You should upgrade the affected component.

## References
- https://gitlab.com/libssh/libssh-mirror/-/commit/855a0853ad3abd4a6cd85ce06fce6d8d4c7a0b60
- https://vuldb.com/?ctiid.349709
- https://vuldb.com/?id.349709
- https://vuldb.com/?submit.767120
- https://www.libssh.org/files/0.12/libssh-0.12.0.tar.xz
- https://www.libssh.org/security/advisories/libssh-2026-sftp-extensions.txt
