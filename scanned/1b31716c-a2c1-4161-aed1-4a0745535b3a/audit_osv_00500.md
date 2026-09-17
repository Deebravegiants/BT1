# [C] ALPINE-CVE-2017-14265

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-14265
Ecosystem: Alpine:v3.7
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14265
Type: osv

## Affected
- Alpine:v3.7: `libraw` — affected >=0 <0.18.5-r0

## Details
A Stack-based Buffer Overflow was discovered in xtrans_interpolate in internal/dcraw_common.cpp in LibRaw before 0.18.3. It could allow a remote denial of service or code execution attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14265
