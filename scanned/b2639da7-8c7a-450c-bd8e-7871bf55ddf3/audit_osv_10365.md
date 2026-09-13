# [H] CVE-2017-15119

## Summary
Severity: High
Advisory: CVE-2017-15119
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-15119
Type: osv

## Details
The Network Block Device (NBD) server in Quick Emulator (QEMU) before 2.11 is vulnerable to a denial of service issue. It could occur if a client sent large option requests, making the server waste CPU time on reading up to 4GB per request. A client could use this flaw to keep the NBD server from serving other requests, resulting in DoS.

## References
- http://www.securityfocus.com/bid/102011
- https://access.redhat.com/errata/RHSA-2018:1104
- https://access.redhat.com/errata/RHSA-2018:1113
- https://lists.gnu.org/archive/html/qemu-devel/2017-11/msg05044.html
- https://usn.ubuntu.com/3575-1/
- https://www.debian.org/security/2018/dsa-4213
- http://www.openwall.com/lists/oss-security/2017/11/28/9
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-15119
