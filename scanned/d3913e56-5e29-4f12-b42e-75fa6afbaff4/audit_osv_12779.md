# [H] CVE-2018-14722

## Summary
Severity: High
Advisory: CVE-2018-14722
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-15
Source: https://osv.dev/vulnerability/CVE-2018-14722
Type: osv

## Details
An issue was discovered in evaluate_auto_mountpoint in btrfsmaintenance-functions in btrfsmaintenance through 0.4.1. Code execution as root can occur via a specially crafted filesystem label if btrfs-{scrub,balance,trim} are set to auto in /etc/sysconfig/btrfsmaintenance (this is not the default, though).

## References
- http://www.openwall.com/lists/oss-security/2019/06/27/7
- http://www.openwall.com/lists/oss-security/2019/06/28/1
- http://www.openwall.com/lists/oss-security/2019/06/28/2
- http://www.openwall.com/lists/oss-security/2018/08/14/7
- https://bugzilla.suse.com/show_bug.cgi?id=1102721
