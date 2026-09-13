# [M] CVE-2021-43528

## Summary
Severity: Medium
Advisory: CVE-2021-43528
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-43528
Type: osv

## Details
Thunderbird unexpectedly enabled JavaScript in the composition area. The JavaScript execution context was limited to this area and did not receive chrome-level privileges, but could be used as a stepping stone to further an attack with other vulnerabilities. This vulnerability affects Thunderbird < 91.4.0.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://security.gentoo.org/glsa/202208-14
- https://www.mozilla.org/security/advisories/mfsa2021-54/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1742579
- https://www.debian.org/security/2022/dsa-5034
