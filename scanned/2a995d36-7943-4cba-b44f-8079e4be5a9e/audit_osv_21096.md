# [M] CVE-2021-40566

## Summary
Severity: Medium
Advisory: CVE-2021-40566
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-40566
Type: osv

## Details
A Segmentation fault casued by heap use after free vulnerability exists in Gpac through 1.0.1 via the mpgviddmx_process function in reframe_mpgvid.c when using mp4box, which causes a denial of service.

## References
- https://github.com/gpac/gpac/issues/1887
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/96047e0e6166407c40cc19f4e94fb35cd7624391
