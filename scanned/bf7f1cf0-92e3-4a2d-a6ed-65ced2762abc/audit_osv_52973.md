# [C] CVE-2022-23303

## Summary
Severity: Critical
Advisory: CVE-2022-23303
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-17
Source: https://osv.dev/vulnerability/CVE-2022-23303
Type: osv

## Details
The implementations of SAE in hostapd before 2.10 and wpa_supplicant before 2.10 are vulnerable to side channel attacks as a result of cache access patterns. NOTE: this issue exists because of an incomplete fix for CVE-2019-9494.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPDHU5MV464CZBPX7N2SNMUYP6DFIBZL/
- https://security.gentoo.org/glsa/202309-16
- https://w1.fi/security/2022-1/
