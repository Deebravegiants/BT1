# [H] CVE-2016-9448

## Summary
Severity: High
Advisory: CVE-2016-9448
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-9448
Type: osv

## Details
The TIFFFetchNormalTag function in LibTiff 4.0.6 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) by setting the tags TIFF_SETGET_C16ASCII or TIFF_SETGET_C32_ASCII to values that access 0-byte arrays.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-9297.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00017.html
- http://www.debian.org/security/2017/dsa-3762
- http://www.openwall.com/lists/oss-security/2016/11/18/15
- http://www.securityfocus.com/bid/94420
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2593
