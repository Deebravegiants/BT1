# [H] CVE-2016-2052

## Summary
Severity: High
Advisory: CVE-2016-2052
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2016-01-25
Source: https://osv.dev/vulnerability/CVE-2016-2052
Type: osv

## Details
Multiple unspecified vulnerabilities in HarfBuzz before 1.0.6, as used in Google Chrome before 48.0.2564.82, allow attackers to cause a denial of service or possibly have other impact via crafted data, as demonstrated by a buffer over-read resulting from an inverted length check in hb-ot-font.cc, a different issue than CVE-2015-8947.

## References
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00070.html
- http://www.securityfocus.com/bid/81812
- http://www.securitytracker.com/id/1034801
- https://code.google.com/p/chromium/issues/detail?id=544270
- https://code.google.com/p/chromium/issues/detail?id=579625
- http://rhn.redhat.com/errata/RHSA-2016-0072.html
- http://www.ubuntu.com/usn/USN-2877-1
- http://www.ubuntu.com/usn/USN-3067-1
- https://security.gentoo.org/glsa/201701-76
- https://github.com/behdad/harfbuzz/issues/139#issuecomment-148289957
- https://github.com/behdad/harfbuzz/commit/63ef0b41dc48d6112d1918c1b1de9de8ea90adb5
- http://googlechromereleases.blogspot.com/2016/01/stable-channel-update_20.html
