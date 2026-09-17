# [M] ALPINE-CVE-2025-22134

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-22134
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-01-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-22134
Type: osv

## Affected
- Alpine:v3.21: `vim` — affected >=0 <9.1.1003-r0
- Alpine:v3.22: `vim` — affected >=0 <9.1.1003-r0
- Alpine:v3.23: `vim` — affected >=0 <9.1.1003-r0

## Details
When switching to other buffers using the :all command and visual mode still being active, this may cause a heap-buffer overflow, because Vim does not properly end visual mode and therefore may try to access beyond the end of a line in a buffer. In Patch 9.1.1003 Vim will correctly reset the visual mode before opening other windows and buffers and therefore fix this bug. In addition it does verify that it won't try to access a position if the position is greater than the corresponding buffer line. Impact is medium since the user must have switched on visual mode when executing the :all ex command. The Vim project would like to thank github user gandalf4a for reporting this issue. The issue has been fixed as of Vim patch v9.1.1003

## References
- https://security.alpinelinux.org/vuln/CVE-2025-22134
