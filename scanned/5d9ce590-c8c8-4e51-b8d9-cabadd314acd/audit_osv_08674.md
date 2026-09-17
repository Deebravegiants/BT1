# [H] CVE-2016-5128

## Summary
Severity: High
Advisory: CVE-2016-5128
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-07-23
Source: https://osv.dev/vulnerability/CVE-2016-5128
Type: osv

## Details
objects.cc in Google V8 before 5.2.361.27, as used in Google Chrome before 52.0.2743.82, does not prevent API interceptors from modifying a store target without setting a property, which allows remote attackers to bypass the Same Origin Policy via a crafted web site.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00028.html
- http://www.securityfocus.com/bid/92053
- http://www.securitytracker.com/id/1036428
- https://codereview.chromium.org/2082633002
- https://codereview.chromium.org/2084183004
- https://codereview.chromium.org/2085223002
- https://codereview.chromium.org/2101983002
- https://codereview.chromium.org/2103033002
- https://crbug.com/619166
- http://rhn.redhat.com/errata/RHSA-2016-1485.html
- http://www.debian.org/security/2016/dsa-3637
- http://www.ubuntu.com/usn/USN-3041-1
- https://security.gentoo.org/glsa/201610-09
- http://googlechromereleases.blogspot.com/2016/07/stable-channel-update.html
