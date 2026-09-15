# [H] CVE-2018-1000001

## Summary
Severity: High
Advisory: CVE-2018-1000001
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-31
Source: https://osv.dev/vulnerability/CVE-2018-1000001
Type: osv

## Details
In glibc 2.26 and earlier there is confusion in the usage of getcwd() by realpath() which can be used to write before the destination buffer leading to a buffer underflow and potential code execution.

## References
- http://seclists.org/oss-sec/2018/q1/38
- http://www.securityfocus.com/bid/102525
- http://www.securitytracker.com/id/1040162
- https://access.redhat.com/errata/RHSA-2018:0805
- https://security.netapp.com/advisory/ntap-20190404-0003/
- https://usn.ubuntu.com/3534-1/
- https://usn.ubuntu.com/3536-1/
- https://www.halfdog.net/Security/2017/LibcRealpathBufferUnderflow/
- https://www.exploit-db.com/exploits/43775/
- https://www.exploit-db.com/exploits/44889/
