# [M] CVE-2018-14335

## Summary
Severity: Medium
Advisory: CVE-2018-14335
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-24
Source: https://osv.dev/vulnerability/CVE-2018-14335
Type: osv

## Details
An issue was discovered in H2 1.4.197. Insecure handling of permissions in the backup function allows attackers to read sensitive files (outside of their permissions) via a symlink to a fake database file.

## References
- https://lists.apache.org/thread.html/582d4165de6507b0be82d5a6f9a1ce392ec43a00c9fed32bacf7fe1e%40%3Cuser.ignite.apache.org%3E
- https://access.redhat.com/errata/RHSA-2020:0727
- https://security.netapp.com/advisory/ntap-20240726-0003/
- https://gist.github.com/owodelta/9714faf9a86435cef5a99d4930eaee20
- https://www.exploit-db.com/exploits/45105/
