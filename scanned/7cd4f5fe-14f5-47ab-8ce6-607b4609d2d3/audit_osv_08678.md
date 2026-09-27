# [M] CVE-2016-5172

## Summary
Severity: Medium
Advisory: CVE-2016-5172
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-09-25
Source: https://osv.dev/vulnerability/CVE-2016-5172
Type: osv

## Details
The parser in Google V8, as used in Google Chrome before 53.0.2785.113, mishandles scopes, which allows remote attackers to obtain sensitive information from arbitrary memory locations via crafted JavaScript code.

## References
- http://www.securityfocus.com/bid/92942
- http://www.securitytracker.com/id/1036826
- https://codereview.chromium.org/2077283004
- https://crbug.com/616386
- http://rhn.redhat.com/errata/RHSA-2016-1905.html
- http://www.debian.org/security/2016/dsa-3667
- https://security.gentoo.org/glsa/201610-09
- https://googlechromereleases.blogspot.com/2016/09/stable-channel-update-for-desktop_13.html
