# [H] CVE-2020-0466

## Summary
Severity: High
Advisory: CVE-2020-0466
Aliases: A-147802478, ASB-A-147802478
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-14
Source: https://osv.dev/vulnerability/CVE-2020-0466
Type: osv

## Details
In do_epoll_ctl and ep_loop_check_proc of eventpoll.c, there is a possible use after free due to a logic error. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-147802478References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2020-12-01
- https://source.android.com/security/bulletin/2020-12-01
