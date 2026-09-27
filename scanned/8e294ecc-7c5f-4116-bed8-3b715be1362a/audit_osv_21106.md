# [M] CVE-2021-40576

## Summary
Severity: Medium
Advisory: CVE-2021-40576
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40576
Type: osv

## Details
The binary MP4Box in Gpac 1.0.1 has a null pointer dereference vulnerability in the gf_isom_get_payt_count function in hint_track.c, which allows attackers to cause a denial of service.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1904
- https://github.com/gpac/gpac/commit/ad18ece95fa064efc0995c4ab2c985f77fb166ec
