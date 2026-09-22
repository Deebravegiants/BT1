# [M] CVE-2018-7689

## Summary
Severity: Medium
Advisory: CVE-2018-7689
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-07
Source: https://osv.dev/vulnerability/CVE-2018-7689
Type: osv

## Details
Lack of permission checks in the InitializeDevelPackage function in openSUSE Open Build Service before 2.9.3 allowed authenticated users to modify packages where they do not have write permissions.

## References
- https://lists.opensuse.org/opensuse-buildservice/2018-06/msg00014.html
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2018-7689
- https://github.com/openSUSE/open-build-service/commit/990ef7cccef6f38fc1d1a1bb22a08e174dcba43b
