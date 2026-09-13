# [M] CVE-2019-20395

## Summary
Severity: Medium
Advisory: CVE-2019-20395
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-01-22
Source: https://osv.dev/vulnerability/CVE-2019-20395
Type: osv

## Details
A stack consumption issue is present in libyang before v1.0-r1 due to the self-referential union type containing leafrefs. Applications that use libyang to parse untrusted input yang files may crash.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00019.html
- https://github.com/CESNET/libyang/commit/4e610ccd87a2ba9413819777d508f71163fcc237
- https://github.com/CESNET/libyang/compare/v0.16-r3...v1.0-r1
- https://bugzilla.redhat.com/show_bug.cgi?id=1793924
- https://github.com/CESNET/libyang/issues/724
