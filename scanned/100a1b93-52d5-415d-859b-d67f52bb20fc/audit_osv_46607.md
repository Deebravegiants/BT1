# [H] CVE-2014-1947

## Summary
Severity: High
Advisory: CVE-2014-1947
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-17
Source: https://osv.dev/vulnerability/CVE-2014-1947
Type: osv

## Details
Stack-based buffer overflow in the WritePSDImage function in coders/psd.c in ImageMagick 6.5.4 and earlier allows remote attackers to cause a denial of service (crash) and possibly execute arbitrary code via a large number of layers in a PSD image, involving the L%02ld string, a different vulnerability than CVE-2014-2030.

## References
- http://www.openwall.com/lists/oss-security/2014/02/12/13
- http://www.openwall.com/lists/oss-security/2014/02/12/2
- http://www.openwall.com/lists/oss-security/2014/02/13/2
- http://www.openwall.com/lists/oss-security/2014/02/13/5
- http://www.openwall.com/lists/oss-security/2014/02/19/13
- https://bugzilla.redhat.com/show_bug.cgi?id=1064098
- https://www.suse.com/support/update/announcement/2014/suse-su-20140359-1.html
- http://www.openwall.com/lists/oss-security/2014/02/12/13
- http://www.openwall.com/lists/oss-security/2014/02/12/2
- http://www.openwall.com/lists/oss-security/2014/02/13/2
- http://www.openwall.com/lists/oss-security/2014/02/13/5
- http://www.openwall.com/lists/oss-security/2014/02/19/13
- http://www.openwall.com/lists/oss-security/2014/02/12/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1064098
