# [M] CVE-2020-12399

## Summary
Severity: Medium
Advisory: CVE-2020-12399
CVSS: 4.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12399
Type: osv

## Details
NSS has shown timing differences when performing DSA signatures, which was exploitable and could eventually leak private keys. This vulnerability affects Thunderbird < 68.9.0, Firefox < 77, and Firefox ESR < 68.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-22/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00029.html
- https://security.gentoo.org/glsa/202007-49
- https://usn.ubuntu.com/4421-1/
- https://www.debian.org/security/2020/dsa-4726
- https://www.mozilla.org/security/advisories/mfsa2020-20/
- https://www.mozilla.org/security/advisories/mfsa2020-21/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1631576
