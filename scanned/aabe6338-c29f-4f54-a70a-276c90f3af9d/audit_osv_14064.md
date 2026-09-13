# [C] CVE-2018-6871

## Summary
Severity: Critical
Advisory: CVE-2018-6871
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-6871
Type: osv

## Details
LibreOffice before 5.4.5 and 6.x before 6.0.1 allows remote attackers to read arbitrary files via =WEBSERVICE calls in a document, which use the COM.MICROSOFT.WEBSERVICE function.

## References
- https://access.redhat.com/errata/RHSA-2018:0418
- https://access.redhat.com/errata/RHSA-2018:0517
- https://usn.ubuntu.com/3579-1/
- https://www.debian.org/security/2018/dsa-4111
- https://www.libreoffice.org/about-us/security/advisories/cve-2018-1055/
- https://cgit.freedesktop.org/libreoffice/core/commit/?h=libreoffice-5-4-5&id=a916fc0c0e0e8b10cb4158fa0fa173fe205d434a
- https://github.com/jollheef/libreoffice-remote-arbitrary-file-disclosure
- https://www.exploit-db.com/exploits/44022/
