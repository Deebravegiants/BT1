# [C] CVE-2016-8649

## Summary
Severity: Critical
Advisory: CVE-2016-8649
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2016-8649
Type: osv

## Details
lxc-attach in LXC before 1.0.9 and 2.x before 2.0.6 allows an attacker inside of an unprivileged container to use an inherited file descriptor, of the host's /proc, to access the rest of the host's filesystem via the openat() family of syscalls.

## References
- http://www.securityfocus.com/bid/94498
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=845465
- https://bugs.launchpad.net/ubuntu/+source/lxc/+bug/1639345
- https://security-tracker.debian.org/tracker/CVE-2016-8649
- https://bugzilla.redhat.com/show_bug.cgi?id=1398242
- https://github.com/lxc/lxc/commit/81f466d05f2a89cb4f122ef7f593ff3f279b165c
