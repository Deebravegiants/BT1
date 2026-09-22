# [M] CVE-2017-2626

## Summary
Severity: Medium
Advisory: CVE-2017-2626
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2626
Type: osv

## Details
It was discovered that libICE before 1.0.9-8 used a weak entropy to generate keys. A local attacker could potentially use this flaw for session hijacking using the information available from the process list.

## References
- http://www.openwall.com/lists/oss-security/2019/07/14/3
- https://lists.debian.org/debian-lts-announce/2019/11/msg00022.html
- http://www.securityfocus.com/bid/96480
- http://www.securitytracker.com/id/1037919
- https://access.redhat.com/errata/RHSA-2017:1865
- https://security.gentoo.org/glsa/201704-03
- https://www.x41-dsec.de/lab/advisories/x41-2017-001-xorg/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2626
- https://cgit.freedesktop.org/xorg/lib/libICE/commit/?id=ff5e59f32255913bb1cdf51441b98c9107ae165b
