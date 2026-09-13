# [H] ALPINE-CVE-2017-13735

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-13735
Ecosystem: Alpine:v3.7
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13735
Type: osv

## Affected
- Alpine:v3.7: `libraw` — affected >=0 <0.18.5-r0

## Details
There is a floating point exception in the kodak_radc_load_raw function in dcraw_common.cpp in LibRaw 0.18.2. It will lead to a remote denial of service attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13735
