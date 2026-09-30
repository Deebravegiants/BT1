# [H] CVE-2018-11790

## Summary
Severity: High
Advisory: CVE-2018-11790
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2018-11790
Type: osv

## Details
When loading a document with Apache Open Office 4.1.5 and earlier with smaller end line termination than the operating system uses, the defect occurs. In this case OpenOffice runs into an Arithmetic Overflow at a string length calculation.

## References
- https://lists.apache.org/thread.html/7394e6b5f78a878bd0c44e9bc9adf90b8cdf49e9adc0f287145aba9b%40%3Ccommits.openoffice.apache.org%3E
- http://www.securityfocus.com/bid/106803
- https://usn.ubuntu.com/3883-1/
- https://www.openoffice.org/security/cves/CVE-2018-11790.html
