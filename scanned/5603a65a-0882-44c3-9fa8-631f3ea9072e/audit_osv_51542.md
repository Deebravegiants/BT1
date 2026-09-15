# [H] CVE-2021-32490

## Summary
Severity: High
Advisory: CVE-2021-32490
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-32490
Type: osv

## Details
A flaw was found in djvulibre-3.5.28 and earlier. An out of bounds write in function DJVU::filter_bv() via crafted djvu file may lead to application crash and other consequences.

## References
- https://www.debian.org/security/2021/dsa-5032
- https://bugzilla.redhat.com/show_bug.cgi?id=1943693
