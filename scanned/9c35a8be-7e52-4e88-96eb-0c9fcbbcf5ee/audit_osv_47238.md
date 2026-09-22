# [H] CVE-2016-1624

## Summary
Severity: High
Advisory: CVE-2016-1624
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-14
Source: https://osv.dev/vulnerability/CVE-2016-1624
Type: osv

## Details
Integer underflow in the ProcessCommandsInternal function in dec/decode.c in Brotli, as used in Google Chrome before 48.0.2564.109, allows remote attackers to cause a denial of service (buffer overflow) or possibly have unspecified other impact via crafted data with brotli compression.

## References
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00119.html
- https://code.google.com/p/chromium/issues/detail?id=583607
- http://www.securityfocus.com/bid/83125
- http://www.securitytracker.com/id/1035183
- https://codereview.chromium.org/1662313002
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00104.html
- http://www.debian.org/security/2016/dsa-3486
- https://security.gentoo.org/glsa/201603-09
- http://rhn.redhat.com/errata/RHSA-2016-0241.html
- http://www.ubuntu.com/usn/USN-2895-1
- http://googlechromereleases.blogspot.com/2016/02/stable-channel-update_9.html
