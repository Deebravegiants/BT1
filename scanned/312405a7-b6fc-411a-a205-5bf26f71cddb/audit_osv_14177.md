# [M] CVE-2018-7688

## Summary
Severity: Medium
Advisory: CVE-2018-7688
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-07
Source: https://osv.dev/vulnerability/CVE-2018-7688
Type: osv

## Details
A missing permission check in the review handling of openSUSE Open Build Service before 2.9.3 allowed all authenticated users to modify sources in projects where they do not have write permissions.

## References
- https://lists.opensuse.org/opensuse-buildservice/2018-06/msg00014.html
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2018-7688
- https://github.com/openSUSE/open-build-service/commit/b15cf19e9e01115f653c76ffdc8f54cd97566553
