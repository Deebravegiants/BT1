# [H] CVE-2021-3246

## Summary
Severity: High
Advisory: CVE-2021-3246
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-20
Source: https://osv.dev/vulnerability/CVE-2021-3246
Type: osv

## Details
A heap buffer overflow vulnerability in msadpcm_decode_block of libsndfile 1.0.30 allows attackers to execute arbitrary code via a crafted WAV file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DLUDCEMMPRA3IYYYHVZUOUZXI65FU37V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T7LNW4AVDVL3BU3N3KGVFLTYFASBVCIF/
- https://lists.debian.org/debian-lts-announce/2021/07/msg00024.html
- https://security.gentoo.org/glsa/202309-11
- https://www.debian.org/security/2021/dsa-4947
- https://github.com/libsndfile/libsndfile/issues/687
