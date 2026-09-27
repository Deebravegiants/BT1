# [H] CVE-2018-9422

## Summary
Severity: High
Advisory: CVE-2018-9422
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-06
Source: https://osv.dev/vulnerability/CVE-2018-9422
Type: osv

## Details
In get_futex_key of futex.c, there is a use-after-free due to improper locking. This could lead to local escalation of privilege with no additional privileges needed. User interaction is not needed for exploitation. Product: Android Versions: Android kernel Android ID: A-74250718 References: Upstream kernel.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://bugzilla.suse.com/show_bug.cgi?id=1102001&_ga=2.244341506.661832603.1561012452-1774095668.1553066022
- https://source.android.com/security/bulletin/2018-07-01
