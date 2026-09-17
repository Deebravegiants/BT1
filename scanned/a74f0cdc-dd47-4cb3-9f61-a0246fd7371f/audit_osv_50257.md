# [M] CVE-2020-0427

## Summary
Severity: Medium
Advisory: CVE-2020-0427
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2020-0427
Type: osv

## Details
In create_pinctrl of core.c, there is a possible out of bounds read due to a use after free. This could lead to local information disclosure with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-140550171

## References
- http://packetstormsecurity.com/files/161229/Kernel-Live-Patch-Security-Notice-LSN-0074-1.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://www.starwindsoftware.com/security/sw-20210325-0005/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00021.html
- https://source.android.com/security/bulletin/pixel/2020-09-01
