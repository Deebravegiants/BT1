# [H] ALPINE-CVE-2016-7044

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7044
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7044
Type: osv

## Affected
- Alpine:v3.2: `irssi` — affected >=0 <0.8.20-r0
- Alpine:v3.3: `irssi` — affected >=0 <0.8.20-r0

## Details
The unformat_24bit_color function in the format parsing code in Irssi before 0.8.20, when compiled with true-color enabled, allows remote attackers to cause a denial of service (heap corruption and crash) via an incomplete 24bit color code.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7044
