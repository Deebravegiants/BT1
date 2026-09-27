# [H] ALPINE-CVE-2019-20421

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-20421
Ecosystem: Alpine:v3.11
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20421
Type: osv

## Affected
- Alpine:v3.11: `exiv2` — affected >=0 <0.27.2-r3

## Details
In Jp2Image::readMetadata() in jp2image.cpp in Exiv2 0.27.2, an input file can result in an infinite loop and hang, with high CPU consumption. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20421
