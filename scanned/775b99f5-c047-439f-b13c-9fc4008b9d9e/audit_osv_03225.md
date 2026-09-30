# [M] ALPINE-CVE-2025-24014

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-24014
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-24014
Type: osv

## Affected
- Alpine:v3.21: `vim` — affected >=0 <9.1.1105-r0
- Alpine:v3.22: `vim` — affected >=0 <9.1.1105-r0
- Alpine:v3.23: `vim` — affected >=0 <9.1.1105-r0

## Details
Vim is an open source, command line text editor. A segmentation fault was found in Vim before 9.1.1043. In silent Ex mode (-s -e), Vim typically doesn't show a screen and just operates silently in batch mode. However, it is still possible to trigger the function that handles the scrolling of a gui version of Vim by feeding some binary characters to Vim. The function that handles the scrolling however may be triggering a redraw, which will access the ScreenLines pointer, even so this variable hasn't been allocated (since there is no screen). This vulnerability is fixed in 9.1.1043.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-24014
