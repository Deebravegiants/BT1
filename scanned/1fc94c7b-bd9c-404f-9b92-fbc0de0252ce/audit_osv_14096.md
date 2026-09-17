# [C] CVE-2018-7186

## Summary
Severity: Critical
Advisory: CVE-2018-7186
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-16
Source: https://osv.dev/vulnerability/CVE-2018-7186
Type: osv

## Details
Leptonica before 1.75.3 does not limit the number of characters in a %s format argument to fscanf or sscanf, which allows remote attackers to cause a denial of service (stack-based buffer overflow) or possibly have unspecified other impact via a long string, as demonstrated by the gplotRead and ptaReadStream functions.

## References
- https://bugs.debian.org/890548
- https://lists.debian.org/debian-lts-announce/2018/03/msg00005.html
- https://lists.debian.org/debian-lts/2018/02/msg00054.html
- https://security.gentoo.org/glsa/202312-01
- https://github.com/DanBloomberg/leptonica/commit/ee301cb2029db8a6289c5295daa42bba7715e99a
