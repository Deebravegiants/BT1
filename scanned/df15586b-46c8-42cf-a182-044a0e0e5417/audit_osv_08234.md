# [M] CVE-2016-1688

## Summary
Severity: Medium
Advisory: CVE-2016-1688
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-06-05
Source: https://osv.dev/vulnerability/CVE-2016-1688
Type: osv

## Details
The regexp (aka regular expression) implementation in Google V8 before 5.0.71.40, as used in Google Chrome before 51.0.2704.63, mishandles external string sizes, which allows remote attackers to cause a denial of service (out-of-bounds read) via crafted JavaScript code.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00005.html
- http://www.securityfocus.com/bid/90876
- http://www.securitytracker.com/id/1035981
- https://codereview.chromium.org/1927003003
- https://crbug.com/604897
- http://www.debian.org/security/2016/dsa-3590
- http://www.ubuntu.com/usn/USN-2992-1
- https://access.redhat.com/errata/RHSA-2016:1190
- https://security.gentoo.org/glsa/201607-07
- http://googlechromereleases.blogspot.com/2016/05/stable-channel-update_25.html
