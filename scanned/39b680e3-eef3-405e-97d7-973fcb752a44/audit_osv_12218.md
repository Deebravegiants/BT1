# [M] CVE-2018-10924

## Summary
Severity: Medium
Advisory: CVE-2018-10924
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-10924
Type: osv

## Details
It was discovered that fsync(2) system call in glusterfs client code leaks memory. An authenticated attacker could use this flaw to launch a denial of service attack by making gluster clients consume memory of the host machine.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00035.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10924
- https://review.gluster.org/#/c/glusterfs/+/20723/
