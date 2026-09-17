# [M] CVE-2019-20632

## Summary
Severity: Medium
Advisory: CVE-2019-20632
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2019-20632
Type: osv

## Details
An issue was discovered in libgpac.a in GPAC before 0.8.0, as demonstrated by MP4Box. It contains an invalid pointer dereference in gf_odf_delete_descriptor in odf/desc_private.c that can cause a denial of service via a crafted MP4 file.

## References
- https://github.com/gpac/gpac/issues/1271
