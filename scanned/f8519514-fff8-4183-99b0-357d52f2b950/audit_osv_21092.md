# [M] CVE-2021-40562

## Summary
Severity: Medium
Advisory: CVE-2021-40562
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-40562
Type: osv

## Details
A Segmentation fault caused by a floating point exception exists in Gpac through 1.0.1 using mp4box via the naludmx_enqueue_or_dispatch function in reframe_nalu.c, which causes a denial of service.

## References
- https://github.com/gpac/gpac/issues/1901
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/5dd71c7201a3e5cf40732d585bfb21c906c171d3
