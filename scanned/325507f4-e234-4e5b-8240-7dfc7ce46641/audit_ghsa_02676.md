# [C] Double free in stack_dst

## Summary
Severity: Critical
Advisory: GHSA-8mjx-h23h-w2pg
CVE: CVE-2021-28034
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-8mjx-h23h-w2pg
Type: github-advisory

## Affected
- crates.io: `stack_dst` — affected >=0 <0.6.1

## Details
Affected versions of stack_dst used a push_inner function that increased the internal length of the array and then called val.clone(). If the val.clone() call panics, the stack could drop an already dropped element or drop uninitialized memory. This issue was fixed in `2a4d538` by increasing the length of the array after elements are cloned.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28034
- https://github.com/thepowersgang/stack_dst-rs/issues/5
- https://github.com/thepowersgang/stack_dst-rs/commit/2a4d538
- https://github.com/thepowersgang/stack_dst-rs/commit/2a4d53809e3000f40085f2b229b6b1a33759881d
- https://github.com/thepowersgang/stack_dst-rs
- https://rustsec.org/advisories/RUSTSEC-2021-0033.html
