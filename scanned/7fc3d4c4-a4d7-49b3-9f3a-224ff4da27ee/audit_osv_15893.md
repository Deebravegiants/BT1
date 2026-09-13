# [M] CVE-2019-20391

## Summary
Severity: Medium
Advisory: CVE-2019-20391
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-22
Source: https://osv.dev/vulnerability/CVE-2019-20391
Type: osv

## Details
An invalid memory access flaw is present in libyang before v1.0-r3 in the function resolve_feature_value() when an if-feature statement is used inside a bit. Applications that use libyang to parse untrusted input yang files may crash.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00019.html
- https://github.com/CESNET/libyang/compare/v1.0-r2...v1.0-r3
- https://bugzilla.redhat.com/show_bug.cgi?id=1793934
- https://github.com/CESNET/libyang/commit/bdb596ddc07596fa212f231135b87d0b9178f6f8
- https://github.com/CESNET/libyang/issues/772
