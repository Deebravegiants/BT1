# [M] ALPINE-CVE-2024-47814

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-47814
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47814
Type: osv

## Affected
- Alpine:v3.21: `vim` — affected >=0 <9.1.0936-r0
- Alpine:v3.22: `vim` — affected >=0 <9.1.0936-r0
- Alpine:v3.23: `vim` — affected >=0 <9.1.0936-r0

## Details
Vim is an open source, command line text editor. A use-after-free was found in Vim < 9.1.0764. When closing a buffer (visible in a window) a BufWinLeave auto command can cause an use-after-free if this auto command happens to re-open the same buffer in a new split window. Impact is low since the user must have intentionally set up such a strange auto command and run some buffer unload commands. However this may lead to a crash. This issue has been addressed in version 9.1.0764 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47814
