# [M] CVE-2021-40567

## Summary
Severity: Medium
Advisory: CVE-2021-40567
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40567
Type: osv

## Details
Segmentation fault vulnerability exists in Gpac through 1.0.1 via the gf_odf_size_descriptor function in desc_private.c when using mp4box, which causes a denial of service.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1889
- https://github.com/gpac/gpac/commit/f5a038e6893019ee471b6a57490cf7a495673816
