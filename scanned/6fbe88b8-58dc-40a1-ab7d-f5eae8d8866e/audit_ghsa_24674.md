# [M] insert_slice_clone can double drop if Clone panics.

## Summary
Severity: Medium
Advisory: GHSA-68p4-pjpf-xwcq
CVE: CVE-2021-26954
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-68p4-pjpf-xwcq
Type: github-advisory

## Affected
- crates.io: `qwutils` — affected >=0 <0.3.1

## Details
Affected versions of this crate used ptr::copy when inserting into the middle of a Vec. When ownership was temporarily duplicated during this copy, it calls the clone method of a user provided element.

This issue can result in an element being double-freed if the clone call panics.

Commit `20cb73d` fixed this issue by adding a set_len(0) call before operating on the vector to avoid dropping the elements during a panic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26954
- https://github.com/qwertz19281/rust_utils/issues/3
- https://github.com/qwertz19281/rust_utils/commit/20cb73d
- https://github.com/qwertz19281/rust_utils
- https://rustsec.org/advisories/RUSTSEC-2021-0018.html
