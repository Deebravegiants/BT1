# [M] ALPINE-CVE-2024-43374

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-43374
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-43374
Type: osv

## Affected
- Alpine:v3.20: `vim` — affected >=0 <9.1.0678-r0
- Alpine:v3.21: `vim` — affected >=0 <9.1.0678-r0
- Alpine:v3.22: `vim` — affected >=0 <9.1.0678-r0
- Alpine:v3.23: `vim` — affected >=0 <9.1.0678-r0

## Details
The UNIX editor Vim prior to version 9.1.0678 has a use-after-free error in argument list handling. When adding a new file to the argument list, this triggers `Buf*` autocommands. If in such an autocommand the buffer that was just opened is closed (including the window where it is shown), this causes the window structure to be freed which contains a reference to the argument list that we are actually modifying. Once the autocommands are completed, the references to the window and argument list are no longer valid and as such cause an use-after-free. Impact is low since the user must either intentionally add some unusual autocommands that wipe a buffer during creation (either manually or by sourcing a malicious plugin), but it will crash Vim. The issue has been fixed as of Vim patch v9.1.0678.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-43374
