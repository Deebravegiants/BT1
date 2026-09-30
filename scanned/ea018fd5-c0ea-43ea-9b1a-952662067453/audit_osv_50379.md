# [H] CVE-2020-14356

## Summary
Severity: High
Advisory: CVE-2020-14356
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-19
Source: https://osv.dev/vulnerability/CVE-2020-14356
Type: osv

## Details
A flaw null pointer dereference in the Linux kernel cgroupv2 subsystem in versions before 5.7.10 was found in the way when reboot the system. A local user could use this flaw to crash the system or escalate their privileges on the system.

## References
- https://usn.ubuntu.com/4484-1/
- https://usn.ubuntu.com/4526-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00047.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://security.netapp.com/advisory/ntap-20200904-0002/
- https://usn.ubuntu.com/4483-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00007.html
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://bugzilla.kernel.org/show_bug.cgi?id=208003
- https://bugzilla.redhat.com/show_bug.cgi?id=1868453
- https://lore.kernel.org/netdev/CAM_iQpUKQJrj8wE+Qa8NGR3P0L+5Uz=qo-O5+k_P60HzTde6aw%40mail.gmail.com/t/
