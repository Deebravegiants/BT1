# [H] CVE-2022-20141

## Summary
Severity: High
Advisory: CVE-2022-20141
Aliases: A-112551163, ASB-A-112551163
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-15
Source: https://osv.dev/vulnerability/CVE-2022-20141
Type: osv

## Details
In ip_check_mc_rcu of igmp.c, there is a possible use after free due to improper locking. This could lead to local escalation of privilege when opening and closing inet sockets with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-112551163References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-06-01
