# [M] CVE-2017-2616

## Summary
Severity: Medium
Advisory: CVE-2017-2616
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2616
Type: osv

## Details
A race condition was found in util-linux before 2.32.1 in the way su handled the management of child processes. A local authenticated attacker could use this flaw to kill other processes with root privileges under specific conditions.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0654.html
- http://www.securityfocus.com/bid/96404
- http://www.securitytracker.com/id/1038271
- https://access.redhat.com/errata/RHSA-2017:0907
- https://security.gentoo.org/glsa/201706-02
- https://www.debian.org/security/2017/dsa-3793
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2616
- https://github.com/karelzak/util-linux/commit/dffab154d29a288aa171ff50263ecc8f2e14a891
