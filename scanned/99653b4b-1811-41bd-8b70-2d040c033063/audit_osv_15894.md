# [M] CVE-2019-20392

## Summary
Severity: Medium
Advisory: CVE-2019-20392
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-22
Source: https://osv.dev/vulnerability/CVE-2019-20392
Type: osv

## Details
An invalid memory access flaw is present in libyang before v1.0-r1 in the function resolve_feature_value() when an if-feature statement is used inside a list key node, and the feature used is not defined. Applications that use libyang to parse untrusted input yang files may crash.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00019.html
- https://github.com/CESNET/libyang/compare/v0.16-r3...v1.0-r1
- https://bugzilla.redhat.com/show_bug.cgi?id=1793922
- https://github.com/CESNET/libyang/commit/32fb4993bc8bb49e93e84016af3c10ea53964be5
- https://github.com/CESNET/libyang/issues/723
