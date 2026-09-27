# [M] CVE-2011-3585

## Summary
Severity: Medium
Advisory: CVE-2011-3585
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-31
Source: https://osv.dev/vulnerability/CVE-2011-3585
Type: osv

## Details
Multiple race conditions in the (1) mount.cifs and (2) umount.cifs programs in Samba 3.6 allow local users to cause a denial of service (mounting outage) via a SIGKILL signal during a time window when the /etc/mtab~ file exists.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=742907
- https://bugzilla.samba.org/show_bug.cgi?id=7179
- https://www.openwall.com/lists/oss-security/2011/09/27/1
- https://www.openwall.com/lists/oss-security/2011/09/30/5
- https://www.openwall.com/lists/oss-security/2011/09/27/1
- https://www.openwall.com/lists/oss-security/2011/09/30/5
- https://bugzilla.redhat.com/show_bug.cgi?id=742907
- https://bugzilla.samba.org/show_bug.cgi?id=7179
- https://git.samba.org/?p=cifs-utils.git%3Ba=commitdiff%3Bh=810f7e4e0f2dbcbee0294d9b371071cb08268200
