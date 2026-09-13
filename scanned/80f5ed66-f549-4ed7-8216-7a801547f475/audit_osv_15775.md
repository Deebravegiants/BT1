# [M] CVE-2019-19624

## Summary
Severity: Medium
Advisory: CVE-2019-19624
Aliases: GHSA-jggw-2q6g-c3m6, PYSEC-2026-2800, PYSEC-2026-2824, PYSEC-2026-2839, PYSEC-2026-723
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2019-12-06
Source: https://osv.dev/vulnerability/CVE-2019-19624
Type: osv

## Details
An out-of-bounds read was discovered in OpenCV before 4.1.1. Specifically, variable coarsest_scale is assumed to be greater than or equal to finest_scale within the calc()/ocl_calc() functions in dis_flow.cpp. However, this is not true when dealing with small images, leading to an out-of-bounds read of the heap-allocated arrays Ux and Uy.

## References
- https://access.redhat.com/security/cve/cve-2019-19624
- https://github.com/opencv/opencv/issues/14554
- https://github.com/opencv/opencv/commit/d1615ba11a93062b1429fce9f0f638d1572d3418
