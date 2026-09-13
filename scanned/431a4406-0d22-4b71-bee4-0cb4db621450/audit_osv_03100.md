# [M] ALPINE-CVE-2024-43790

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-43790
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-43790
Type: osv

## Affected
- Alpine:v3.20: `vim` — affected >=9.1.0425 <9.1.0707-r0
- Alpine:v3.21: `vim` — affected >=9.1.0425 <9.1.0707-r0
- Alpine:v3.22: `vim` — affected >=9.1.0425 <9.1.0707-r0
- Alpine:v3.23: `vim` — affected >=9.1.0425 <9.1.0707-r0

## Details
Vim is an open source command line text editor. When performing a search and displaying the search-count message is disabled (:set shm+=S), the search pattern is displayed at the bottom of the screen in a buffer (msgbuf). When right-left mode (:set rl) is enabled, the search pattern is reversed. This happens by allocating a new buffer. If the search pattern contains some ASCII NUL characters, the buffer allocated will be smaller than the original allocated buffer (because for allocating the reversed buffer, the strlen() function is called, which only counts until it notices an ASCII NUL byte ) and thus the original length indicator is wrong. This causes an overflow when accessing characters inside the msgbuf by the previously (now wrong) length of the msgbuf. The issue has been fixed as of Vim patch v9.1.0689.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-43790
