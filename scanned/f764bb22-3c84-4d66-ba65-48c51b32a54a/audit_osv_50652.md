# [M] CVE-2020-27066

## Summary
Severity: Medium
Advisory: CVE-2020-27066
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-27066
Type: osv

## Details
In xfrm6_tunnel_free_spi of net/ipv6/xfrm6_tunnel.c, there is a possible use after free due to improper locking. This could lead to local escalation of privilege with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-168043318

## References
- https://source.android.com/security/bulletin/pixel/2020-12-01
- https://source.android.com/security/bulletin/pixel/2020-12-01
