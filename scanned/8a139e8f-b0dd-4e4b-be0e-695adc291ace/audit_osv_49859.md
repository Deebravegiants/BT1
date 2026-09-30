# [H] CVE-2019-1999

## Summary
Severity: High
Advisory: CVE-2019-1999
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2019-1999
Type: osv

## Details
In binder_alloc_free_page of binder_alloc.c, there is a possible double free due to improper locking. This could lead to local escalation of privilege in the kernel with no additional execution privileges needed. User interaction is not needed for exploitation. Product: Android. Versions: Android kernel. Android ID: A-120025196.

## References
- http://www.securityfocus.com/bid/106851
- https://seclists.org/bugtraq/2019/Aug/13
- https://source.android.com/security/bulletin/2019-02-01
- https://usn.ubuntu.com/3979-1/
- https://www.debian.org/security/2019/dsa-4495
- https://www.exploit-db.com/exploits/46357/
