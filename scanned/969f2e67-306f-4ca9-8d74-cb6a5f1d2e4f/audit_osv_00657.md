# [H] ALPINE-CVE-2017-5356

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5356
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5356
Type: osv

## Affected
- Alpine:v3.2: `irssi` — affected >=0 <0.8.21-r0
- Alpine:v3.3: `irssi` — affected >=0 <0.8.21-r0
- Alpine:v3.4: `irssi` — affected >=0 <0.8.21-r0
- Alpine:v3.5: `irssi` — affected >=0 <0.8.21-r0

## Details
Irssi before 0.8.21 allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a string containing a formatting sequence (%[) without a closing bracket (]).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5356
