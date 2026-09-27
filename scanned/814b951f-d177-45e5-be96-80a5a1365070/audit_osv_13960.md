# [M] CVE-2018-5783

## Summary
Severity: Medium
Advisory: CVE-2018-5783
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-19
Source: https://osv.dev/vulnerability/CVE-2018-5783
Type: osv

## Details
In PoDoFo 0.9.5, there is an uncontrolled memory allocation in the PoDoFo::PdfVecObjects::Reserve function (base/PdfVecObjects.h). Remote attackers could leverage this vulnerability to cause a denial of service via a crafted pdf file.

## References
- https://sourceforge.net/p/podofo/tickets/27/
- https://bugzilla.redhat.com/show_bug.cgi?id=1536179
