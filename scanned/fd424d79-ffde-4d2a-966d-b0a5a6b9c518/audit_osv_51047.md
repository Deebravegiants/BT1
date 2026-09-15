# [M] CVE-2021-0605

## Summary
Severity: Medium
Advisory: CVE-2021-0605
Aliases: A-110373476, PUB-A-110373476
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-22
Source: https://osv.dev/vulnerability/CVE-2021-0605
Type: osv

## Details
In pfkey_dump of af_key.c, there is a possible out-of-bounds read due to a missing bounds check. This could lead to local information disclosure in the kernel with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-110373476

## References
- https://source.android.com/security/bulletin/pixel/2021-06-01
