# [M] CVE-2018-19149

## Summary
Severity: Medium
Advisory: CVE-2018-19149
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-10
Source: https://osv.dev/vulnerability/CVE-2018-19149
Type: osv

## Details
Poppler before 0.70.0 has a NULL pointer dereference in _poppler_attachment_new when called from poppler_annot_file_attachment_get_attachment.

## References
- http://www.securityfocus.com/bid/106031
- https://access.redhat.com/errata/RHSA-2019:2022
- https://security.gentoo.org/glsa/201904-04
- https://usn.ubuntu.com/3837-1/
- https://usn.ubuntu.com/3837-2/
- https://gitlab.freedesktop.org/poppler/poppler/issues/664
