# [H] CVE-2020-25654

## Summary
Severity: High
Advisory: CVE-2020-25654
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/CVE-2020-25654
Type: osv

## Details
An ACL bypass flaw was found in pacemaker. An attacker having a local account on the cluster and in the haclient group could use IPC communication with various daemons directly to perform certain tasks that they would be prevented by ACLs from doing if they went through the configuration.

## References
- https://lists.clusterlabs.org/pipermail/users/2020-October/027840.html
- https://lists.debian.org/debian-lts-announce/2021/01/msg00007.html
- https://seclists.org/oss-sec/2020/q4/83
- https://security.gentoo.org/glsa/202309-09
- https://bugzilla.redhat.com/show_bug.cgi?id=1888191
