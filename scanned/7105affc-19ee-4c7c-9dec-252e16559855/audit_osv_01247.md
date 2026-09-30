# [C] ALPINE-CVE-2018-7263

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-7263
Ecosystem: Alpine:v3.11
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7263
Type: osv

## Affected
- Alpine:v3.11: `libmad` — affected >=0 <0.15.1b-r9

## Details
The mad_decoder_run() function in decoder.c in Underbit libmad through 0.15.1b allows remote attackers to cause a denial of service (SIGABRT because of double free or corruption) or possibly have unspecified other impact via a crafted file. NOTE: this may overlap CVE-2017-11552.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7263
