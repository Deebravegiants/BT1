# [H] CVE-2020-12420

## Summary
Severity: High
Advisory: CVE-2020-12420
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12420
Type: osv

## Details
When trying to connect to a STUN server, a race condition could have caused a use-after-free of a pointer, leading to memory corruption and a potentially exploitable crash. This vulnerability affects Firefox ESR < 68.10, Firefox < 78, and Thunderbird < 68.10.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00049.html
- https://www.mozilla.org/security/advisories/mfsa2020-24/
- https://www.mozilla.org/security/advisories/mfsa2020-25/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00027.html
- https://security.gentoo.org/glsa/202007-09
- https://security.gentoo.org/glsa/202007-10
- https://usn.ubuntu.com/4421-1/
- https://www.mozilla.org/security/advisories/mfsa2020-26/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00026.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1643437
