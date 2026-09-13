# [H] Data races in bunch

## Summary
Severity: High
Advisory: GHSA-jwph-qp5h-f9wj
CVE: CVE-2020-36450
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jwph-qp5h-f9wj
Type: github-advisory

## Affected
- crates.io: `bunch` — affected >=0

## Details
An issue was discovered in the bunch crate through 2020-11-12 for Rust. 
Affected versions of this crate unconditionally implements `Send`/`Sync` for `Bunch<T>`.
This allows users to insert `T: !Sync` to `Bunch<T>`. It is possible to create a data race to a `T: !Sync` by invoking the `Bunch::get()` API (which returns `&T`) from multiple threads. It is also possible to send `T: !Send` to other threads by inserting `T` inside `Bunch<T>` and sending `Bunch<T>` to another thread, allowing to create a data race by inserting types like `T = Rc<_>`.

Such data races can lead to memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36450
- https://github.com/krl/bunch/issues/1
- https://github.com/krl/bunch
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/bunch/RUSTSEC-2020-0130.md
- https://rustsec.org/advisories/RUSTSEC-2020-0130.html
