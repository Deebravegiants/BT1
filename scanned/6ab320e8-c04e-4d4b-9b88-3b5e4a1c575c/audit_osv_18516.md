# [M] CVE-2020-28049

## Summary
Severity: Medium
Advisory: CVE-2020-28049
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-11-04
Source: https://osv.dev/vulnerability/CVE-2020-28049
Type: osv

## Details
An issue was discovered in SDDM before 0.19.0. It incorrectly starts the X server in a way that - for a short time period - allows local unprivileged users to create a connection to the X server without providing proper authentication. A local attacker can thus access X server display contents and, for example, intercept keystrokes or access the clipboard. This is caused by a race condition during Xauthority file creation.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GT3EX5NSQJJAKY63ENSMEDX6NYZLYY3S/
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00031.html
- https://github.com/sddm/sddm/blob/v0.19.0/ChangeLog
- https://github.com/sddm/sddm/releases
- https://lists.debian.org/debian-lts-announce/2020/11/msg00009.html
- https://security.gentoo.org/glsa/202402-02
- https://www.debian.org/security/2020/dsa-4783
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2020-28049
