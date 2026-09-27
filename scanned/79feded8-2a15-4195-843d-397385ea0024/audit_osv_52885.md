# [M] CVE-2022-20153

## Summary
Severity: Medium
Advisory: CVE-2022-20153
Aliases: A-222091980, PUB-A-222091980
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-15
Source: https://osv.dev/vulnerability/CVE-2022-20153
Type: osv

## Details
In rcu_cblist_dequeue of rcu_segcblist.c, there is a possible use-after-free due to improper locking. This could lead to local escalation of privilege in the kernel with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-222091980References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2022-06-01
