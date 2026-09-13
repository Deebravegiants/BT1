# [M] CVE-2021-39636

## Summary
Severity: Medium
Advisory: CVE-2021-39636
Aliases: A-120612905, PUB-A-120612905
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-39636
Type: osv

## Details
In do_ipt_get_ctl and do_ipt_set_ctl of ip_tables.c, there is a possible way to leak kernel information due to uninitialized data. This could lead to local information disclosure with system execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-120612905References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2021-12-01
- https://source.android.com/security/bulletin/pixel/2021-12-01
