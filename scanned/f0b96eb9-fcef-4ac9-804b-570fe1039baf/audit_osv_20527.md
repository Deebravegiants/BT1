# [M] CVE-2021-3467

## Summary
Severity: Medium
Advisory: CVE-2021-3467
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-25
Source: https://osv.dev/vulnerability/CVE-2021-3467
Type: osv

## Details
A NULL pointer dereference flaw was found in the way Jasper versions before 2.0.26 handled component references in CDEF box in the JP2 image format decoder. A specially crafted JP2 image file could cause an application using the Jasper library to crash when opened.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KWAIUFNIUCGS2IMGGDTWZIUIY7BNLGKF/
- https://bugzilla.redhat.com/show_bug.cgi?id=1942097
