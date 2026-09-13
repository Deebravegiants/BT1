# [H] ALPINE-CVE-2017-12678

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12678
Ecosystem: Alpine:v3.10, Alpine:v3.11
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12678
Type: osv

## Affected
- Alpine:v3.10: `taglib` — affected >=0 <1.11.1-r2
- Alpine:v3.11: `taglib` — affected >=0 <1.11.1-r2

## Details
In TagLib 1.11.1, the rebuildAggregateFrames function in id3v2framefactory.cpp has a pointer to cast vulnerability, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via a crafted audio file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12678
