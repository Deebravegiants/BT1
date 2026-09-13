# [M] crossbeam-channel Vulnerable to Double Free on Drop

## Summary
Severity: Medium
Advisory: GHSA-pg9f-39pc-qf8g
CVE: CVE-2025-4574
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-pg9f-39pc-qf8g
Type: github-advisory

## Affected
- crates.io: `crossbeam-channel` — affected >=0.5.12 <0.5.15

## Details
The internal `Channel` type's `Drop` method has a race
which could, in some circumstances, lead to a double-free.
This could result in memory corruption.

Quoting from the
[upstream description in merge request \#1187](https://github.com/crossbeam-rs/crossbeam/pull/1187#issue-2980761131):

> The problem lies in the fact that `dicard_all_messages` contained two paths that could lead to `head.block` being read but only one of them would swap the value. This meant that `dicard_all_messages` could end up observing a non-null block pointer (and therefore attempting to free it) without setting `head.block` to null. This would then lead to `Channel::drop` making a second attempt at dropping the same pointer.

The bug was introduced while fixing a memory leak, in
upstream [MR \#1084](https://github.com/crossbeam-rs/crossbeam/pull/1084),
first published in 0.5.12.

The fix is in
upstream [MR \#1187](https://github.com/crossbeam-rs/crossbeam/pull/1187)
and has been published in 0.5.15

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-4574
- https://github.com/crossbeam-rs/crossbeam/pull/1187
- https://access.redhat.com/security/cve/CVE-2025-4574
- https://bugzilla.redhat.com/show_bug.cgi?id=2358890
- https://github.com/crossbeam-rs/crossbeam
- https://rustsec.org/advisories/RUSTSEC-2025-0024.html
