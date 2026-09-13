# [H] ALPINE-CVE-2020-0034

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-0034
Ecosystem: Alpine:v3.11
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-0034
Type: osv

## Affected
- Alpine:v3.11: `libvpx` — affected >=0 <1.8.2-r0

## Details
In vp8_decode_frame of decodeframe.c, there is a possible out of bounds read due to improper input validation. This could lead to remote information disclosure if error correction were turned on, with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-8.0 Android-8.1Android ID: A-62458770

## References
- https://security.alpinelinux.org/vuln/CVE-2020-0034
