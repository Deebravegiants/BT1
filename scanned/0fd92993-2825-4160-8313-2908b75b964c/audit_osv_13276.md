# [C] CVE-2018-19047

## Summary
Severity: Critical
Advisory: CVE-2018-19047
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-19047
Type: osv

## Details
mPDF through 7.1.6, if deployed as a web application that accepts arbitrary HTML, allows SSRF, as demonstrated by a '<img src="http://192.168' substring that triggers a call to getImage in Image/ImageProcessor.php. NOTE: the software maintainer disputes this, stating "If you allow users to pass HTML without sanitising it, you're asking for trouble.

## References
- https://github.com/mpdf/mpdf/issues/867
