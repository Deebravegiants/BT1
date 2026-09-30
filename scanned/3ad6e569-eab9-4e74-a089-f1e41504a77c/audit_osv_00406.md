# [M] ALPINE-CVE-2017-11552

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-11552
Ecosystem: Alpine:v3.11
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-11552
Type: osv

## Affected
- Alpine:v3.11: `libmad` — affected >=0 <0.15.1b-r9

## Details
mpg321.c in mpg321 0.3.2-1 does not properly manage memory for use with libmad 0.15.1b, which allows remote attackers to cause a denial of service (memory corruption seen in a crash in the mad_decoder_run function in decoder.c in libmad) via a crafted MP3 file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-11552
