# [M] CVE-2019-20398

## Summary
Severity: Medium
Advisory: CVE-2019-20398
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-22
Source: https://osv.dev/vulnerability/CVE-2019-20398
Type: osv

## Details
A NULL pointer dereference is present in libyang before v1.0-r3 in the function lys_extension_instances_free() due to a copy of unresolved extensions in lys_restr_dup(). Applications that use libyang to parse untrusted input yang files may crash.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00019.html
- https://github.com/CESNET/libyang/compare/v1.0-r2...v1.0-r3
- https://bugzilla.redhat.com/show_bug.cgi?id=1793935
- https://github.com/CESNET/libyang/commit/7852b272ef77f8098c35deea6c6f09cb78176f08
- https://github.com/CESNET/libyang/issues/773
