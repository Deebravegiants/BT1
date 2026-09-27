# [C] CVE-2017-15118

## Summary
Severity: Critical
Advisory: CVE-2017-15118
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-15118
Type: osv

## Details
A stack-based buffer overflow vulnerability was found in NBD server implementation in qemu before 2.11 allowing a client to request an export name of size up to 4096 bytes, which in fact should be limited to 256 bytes, causing an out-of-bounds stack write in the qemu process. If NBD server requires TLS, the attacker cannot trigger the buffer overflow without first successfully negotiating TLS.

## References
- http://www.securityfocus.com/bid/101975
- https://access.redhat.com/errata/RHSA-2018:1104
- https://usn.ubuntu.com/3575-1/
- http://www.openwall.com/lists/oss-security/2017/11/28/8
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-15118
- https://lists.gnu.org/archive/html/qemu-devel/2017-11/msg05045.html
- https://www.exploit-db.com/exploits/43194/
