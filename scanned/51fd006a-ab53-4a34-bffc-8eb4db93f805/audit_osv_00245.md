# [H] ALPINE-CVE-2016-7952

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7952
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7952
Type: osv

## Affected
- Alpine:v3.2: `libxtst` — affected >=0 <1.2.2-r1
- Alpine:v3.3: `libxtst` — affected >=0 <1.2.2-r1

## Details
X.org libXtst before 1.2.3 allows remote X servers to cause a denial of service (infinite loop) via a reply in the (1) XRecordStartOfData, (2) XRecordEndOfData, or (3) XRecordClientDied category without a client sequence and with attached data.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7952
