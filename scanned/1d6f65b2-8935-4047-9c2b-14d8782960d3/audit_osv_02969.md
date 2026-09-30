# [M] ALPINE-CVE-2024-10573

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-10573
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-10573
Type: osv

## Affected
- Alpine:v3.21: `mpg123` — affected >=0 <1.32.8-r0
- Alpine:v3.22: `mpg123` — affected >=0 <1.32.8-r0
- Alpine:v3.23: `mpg123` — affected >=0 <1.32.8-r0
- Alpine:v3.24: `mpg123` — affected >=0 <1.32.8-r0

## Details
An out-of-bounds write flaw was found in mpg123 when handling crafted streams. When decoding PCM, the libmpg123 may write past the end of a heap-located buffer. Consequently, heap corruption may happen, and arbitrary code execution is not discarded. The complexity required to exploit this flaw is considered high as the payload must be validated by the MPEG decoder and the PCM synth before execution. Additionally, to successfully execute the attack, the user must scan through the stream, making web live stream content (such as web radios) a very unlikely attack vector.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-10573
