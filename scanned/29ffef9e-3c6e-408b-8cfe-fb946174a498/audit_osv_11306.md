# [H] CVE-2017-7322

## Summary
Severity: High
Advisory: CVE-2017-7322
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-30
Source: https://osv.dev/vulnerability/CVE-2017-7322
Type: osv

## Details
The (1) update and (2) package-installation features in MODX Revolution 2.5.4-pl and earlier do not verify X.509 certificates from SSL servers, which allows man-in-the-middle attackers to spoof servers and trigger the execution of arbitrary code via a crafted certificate.

## References
- http://www.securityfocus.com/bid/97228
- https://mazinahmed.net/services/public-reports/ModX%20-%20Responsible%20Disclosure%20-%20January%202017.pdf
