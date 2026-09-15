# [M] CVE-2021-30469

## Summary
Severity: Medium
Advisory: CVE-2021-30469
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-30469
Type: osv

## Details
A flaw was found in PoDoFo 0.9.7. An use-after-free in PoDoFo::PdfVecObjects::Clear() function can cause a denial of service via a crafted PDF file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1947433
