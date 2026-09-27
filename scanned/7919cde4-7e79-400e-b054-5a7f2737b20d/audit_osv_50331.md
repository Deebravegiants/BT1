# [M] CVE-2020-12421

## Summary
Severity: Medium
Advisory: CVE-2020-12421
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12421
Type: osv

## Details
When performing add-on updates, certificate chains terminating in non-built-in-roots were rejected (even if they were legitimately added by an administrator.) This could have caused add-ons to become out-of-date silently without notification to the user. This vulnerability affects Firefox ESR < 68.10, Firefox < 78, and Thunderbird < 68.10.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00027.html
- https://security.gentoo.org/glsa/202007-10
- https://www.mozilla.org/security/advisories/mfsa2020-25/
- https://www.mozilla.org/security/advisories/mfsa2020-26/
- https://usn.ubuntu.com/4421-1/
- https://www.mozilla.org/security/advisories/mfsa2020-24/
- https://security.gentoo.org/glsa/202007-09
- https://bugzilla.mozilla.org/show_bug.cgi?id=1308251
