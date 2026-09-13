# [H] CVE-2014-1958

## Summary
Severity: High
Advisory: CVE-2014-1958
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-06
Source: https://osv.dev/vulnerability/CVE-2014-1958
Type: osv

## Details
Buffer overflow in the DecodePSDPixels function in coders/psd.c in ImageMagick before 6.8.8-5 might allow remote attackers to execute arbitrary code via a crafted PSD image, involving the L%06ld string, a different vulnerability than CVE-2014-2030.

## References
- http://lists.opensuse.org/opensuse-updates/2014-03/msg00032.html
- http://lists.opensuse.org/opensuse-updates/2014-03/msg00039.html
- http://ubuntu.com/usn/usn-2132-1
- http://www.openwall.com/lists/oss-security/2014/02/13/2
- http://www.openwall.com/lists/oss-security/2014/02/13/5
- https://www.openwall.com/lists/oss-security/2014/02/19/13
- http://lists.opensuse.org/opensuse-updates/2014-03/msg00032.html
- http://lists.opensuse.org/opensuse-updates/2014-03/msg00039.html
- http://www.openwall.com/lists/oss-security/2014/02/13/2
- http://www.openwall.com/lists/oss-security/2014/02/13/5
- https://www.openwall.com/lists/oss-security/2014/02/19/13
- http://trac.imagemagick.org/changeset/14801
