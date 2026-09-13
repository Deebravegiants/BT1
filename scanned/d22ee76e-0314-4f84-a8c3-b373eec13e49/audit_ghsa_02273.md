# [H] Data races in rcu_cell

## Summary
Severity: High
Advisory: GHSA-686h-j8r8-wmfm
CVE: CVE-2020-36451
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-686h-j8r8-wmfm
Type: github-advisory

## Affected
- crates.io: `rcu_cell` — affected >=0 <0.1.9

## Details
Affected versions of this crate unconditionally implement Send/Sync for `RcuCell<T>`.
This allows users to send `T: !Send` to other threads (while `T` enclosed within `RcuCell<T>`), and allows users to concurrently access `T: !Sync` by using the APIs of `RcuCell<T>` that provide access to `&T`.

This can result in memory corruption caused by data races.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36451
- https://github.com/Xudong-Huang/rcu_cell/issues/3
- https://github.com/Xudong-Huang/rcu_cell/pull/4
- https://github.com/Xudong-Huang/rcu_cell/pull/4/commits/1faf18eee11f14969b77ae0f76dcd9ebd437d0c2
- https://github.com/Xudong-Huang/rcu_cell
- https://rustsec.org/advisories/RUSTSEC-2020-0131.html
