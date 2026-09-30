# [H] CVE-2018-1088

## Summary
Severity: High
Advisory: CVE-2018-1088
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-18
Source: https://osv.dev/vulnerability/CVE-2018-1088
Type: osv

## Details
A privilege escalation flaw was found in gluster 3.x snapshot scheduler. Any gluster client allowed to mount gluster volumes could also mount shared gluster storage volume and escalate privileges by scheduling malicious cronjob via symlink.

## References
- https://access.redhat.com/errata/RHSA-2018:1136
- https://access.redhat.com/errata/RHSA-2018:1137
- https://access.redhat.com/errata/RHSA-2018:1275
- https://access.redhat.com/errata/RHSA-2018:1524
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1558721
