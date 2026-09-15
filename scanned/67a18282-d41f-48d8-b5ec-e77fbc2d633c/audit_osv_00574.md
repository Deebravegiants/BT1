# [M] ALPINE-CVE-2017-16910

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-16910
Ecosystem: Alpine:v3.7
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16910
Type: osv

## Affected
- Alpine:v3.7: `libraw` — affected >=0 <0.18.6-r0

## Details
An error within the "LibRaw::xtrans_interpolate()" function (internal/dcraw_common.cpp) in LibRaw versions prior to 0.18.6 can be exploited to cause an invalid read memory access and subsequently a Denial of Service condition.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16910
