# [H] CVE-2020-25693

## Summary
Severity: High
Advisory: CVE-2020-25693
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-12-03
Source: https://osv.dev/vulnerability/CVE-2020-25693
Type: osv

## Details
A flaw was found in CImg in versions prior to 2.9.3. Integer overflows leading to heap buffer overflows in load_pnm() can be triggered by a specially crafted input file processed by CImg, which can lead to an impact to application availability or data integrity.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ERBZALTF7LXN2LZLPGAUSVMV53GHHTUC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MJ5Q7NNUPXATTBUKHFKIYYAV5GJDYCZL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QZ3NPLYXZWEL7HETIFZVCXEZZ2WYYRWA/
- https://bugzilla.redhat.com/show_bug.cgi?id=1893377
