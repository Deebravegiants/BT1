# [H] CVE-2021-39714

## Summary
Severity: High
Advisory: CVE-2021-39714
Aliases: A-205573273, PUB-A-205573273
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-16
Source: https://osv.dev/vulnerability/CVE-2021-39714
Type: osv

## Details
In ion_buffer_kmap_get of ion.c, there is a possible use-after-free due to an integer overflow. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-205573273References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-08-01
- https://source.android.com/security/bulletin/pixel/2022-08-01
