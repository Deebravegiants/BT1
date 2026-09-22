# [H] CVE-2018-10852

## Summary
Severity: High
Advisory: CVE-2018-10852
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-10852
Type: osv

## Details
The UNIX pipe which sudo uses to contact SSSD and read the available sudo rules from SSSD has too wide permissions, which means that anyone who can send a message using the same raw protocol that sudo and SSSD use can read the sudo rules available for any user. This affects versions of SSSD before 1.16.3.

## References
- http://www.securityfocus.com/bid/104547
- https://access.redhat.com/errata/RHSA-2018:3158
- https://lists.debian.org/debian-lts-announce/2018/07/msg00019.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10852
