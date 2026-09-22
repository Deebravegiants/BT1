# [M] CVE-2014-9645

## Summary
Severity: Medium
Advisory: CVE-2014-9645
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-03-12
Source: https://osv.dev/vulnerability/CVE-2014-9645
Type: osv

## Details
The add_probe function in modutils/modprobe.c in BusyBox before 1.23.0 allows local users to bypass intended restrictions on loading kernel modules via a / (slash) character in a module name, as demonstrated by an "ifconfig /usbserial up" command or a "mount -t /snd_pcm none /" command.

## References
- http://git.busybox.net/busybox/commit/?id=4e314faa0aecb66717418e9a47a4451aec59262b
- http://openwall.com/lists/oss-security/2015/01/24/4
- https://plus.google.com/+MathiasKrause/posts/PqFCo4bfrWu
- https://security.gentoo.org/glsa/201503-13
- http://openwall.com/lists/oss-security/2015/01/24/4
- http://git.busybox.net/busybox/commit/?id=4e314faa0aecb66717418e9a47a4451aec59262b
- http://openwall.com/lists/oss-security/2015/01/24/4
- https://plus.google.com/+MathiasKrause/posts/PqFCo4bfrWu
- http://git.busybox.net/busybox/commit/?id=4e314faa0aecb66717418e9a47a4451aec59262b
- https://bugs.busybox.net/show_bug.cgi?id=7652
- https://bugzilla.redhat.com/show_bug.cgi?id=1185707
- http://seclists.org/fulldisclosure/2020/Mar/15
- http://www.securityfocus.com/bid/72324
- https://lists.debian.org/debian-lts-announce/2018/07/msg00037.html
- https://usn.ubuntu.com/3935-1/
