# [M] CVE-2021-39633

## Summary
Severity: Medium
Advisory: CVE-2021-39633
Aliases: A-150694665, ASB-A-150694665
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-39633
Type: osv

## Details
In gre_handle_offloads of ip_gre.c, there is a possible page fault due to an invalid memory access. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-150694665References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-01-01
- https://source.android.com/security/bulletin/2022-01-01
