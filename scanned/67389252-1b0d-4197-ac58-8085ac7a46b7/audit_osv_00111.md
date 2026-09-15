# [H] ALPINE-CVE-2016-4472

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-4472
Ecosystem: Alpine:v3.4
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-4472
Type: osv

## Affected
- Alpine:v3.4: `expat` — affected >=0 <2.1.1-r2

## Details
The overflow protection in Expat is removed by compilers with certain optimization settings, which allows remote attackers to cause a denial of service (crash) or possibly execute arbitrary code via crafted XML data.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2015-1283 and CVE-2015-2716.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-4472
