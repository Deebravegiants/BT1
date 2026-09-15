# [H] CVE-2017-13216

## Summary
Severity: High
Advisory: CVE-2017-13216
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-12
Source: https://osv.dev/vulnerability/CVE-2017-13216
Type: osv

## Details
In ashmem_ioctl of ashmem.c, there is an out-of-bounds write due to insufficient locking when accessing asma. This could lead to a local elevation of privilege enabling code execution as a privileged process with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android. Versions: Android kernel. Android ID: A-66954097.

## References
- http://www.securityfocus.com/bid/102390
- http://www.securitytracker.com/id/1040106
- https://source.android.com/security/bulletin/2018-01-01
- https://www.exploit-db.com/exploits/43464/
