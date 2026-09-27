# [H] CVE-2018-19963

## Summary
Severity: High
Advisory: CVE-2018-19963
CVSS: 7.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-12-08
Source: https://osv.dev/vulnerability/CVE-2018-19963
Type: osv

## Details
An issue was discovered in Xen 4.11 allowing HVM guest OS users to cause a denial of service (host OS crash) or possibly gain host OS privileges because x86 IOREQ server resource accounting (for external emulators) was mishandled.

## References
- http://www.securityfocus.com/bid/106182
- https://xenbits.xen.org/xsa/advisory-276.html
