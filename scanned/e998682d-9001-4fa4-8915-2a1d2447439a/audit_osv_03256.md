# [M] ALPINE-CVE-2025-29768

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-29768
Ecosystem: Alpine:v3.22, Alpine:v3.23
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-03-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-29768
Type: osv

## Affected
- Alpine:v3.22: `vim` — affected >=0 <9.1.1202-r0
- Alpine:v3.23: `vim` — affected >=0 <9.1.1202-r0

## Details
Vim, a text editor, is vulnerable to potential data loss with zip.vim and special crafted zip files in versions prior to 9.1.1198. The impact is medium because a user must be made to view such an archive with Vim and then press 'x' on such a strange filename. The issue has been fixed as of Vim patch v9.1.1198.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-29768
