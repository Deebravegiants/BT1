# [H] CVE-2021-0929

## Summary
Severity: High
Advisory: CVE-2021-0929
Aliases: A-187527909, ASB-A-187527909
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-0929
Type: osv

## Details
In ion_dma_buf_end_cpu_access and related functions of ion.c, there is a possible way to corrupt memory due to a use after free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-187527909References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2021-11-01
