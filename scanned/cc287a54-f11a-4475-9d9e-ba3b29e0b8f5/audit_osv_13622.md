# [M] CVE-2018-20551

## Summary
Severity: Medium
Advisory: CVE-2018-20551
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-28
Source: https://osv.dev/vulnerability/CVE-2018-20551
Type: osv

## Details
A reachable Object::getString assertion in Poppler 0.72.0 allows attackers to cause a denial of service due to construction of invalid rich media annotation assets in the AnnotRichMedia class in Annot.c.

## References
- https://access.redhat.com/errata/RHSA-2019:2713
- https://usn.ubuntu.com/3886-1/
- https://gitlab.freedesktop.org/poppler/poppler/merge_requests/146
- https://gitlab.freedesktop.org/poppler/poppler/issues/703
