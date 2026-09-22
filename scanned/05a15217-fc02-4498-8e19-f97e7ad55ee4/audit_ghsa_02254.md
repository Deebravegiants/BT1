# [C] Double free in smallvec

## Summary
Severity: Critical
Advisory: GHSA-mm7v-vpv8-xfc3
CVE: CVE-2019-15551
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mm7v-vpv8-xfc3
Type: github-advisory

## Affected
- crates.io: `smallvec` — affected >=0.6.5 <0.6.10

## Details
Attempting to call grow on a spilled SmallVec with a value equal to the current capacity causes it to free the existing data. This performs a double free immediately and may lead to use-after-free on subsequent accesses to the SmallVec contents. An attacker that controls the value passed to grow may exploit this flaw to obtain memory contents or gain remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15551
- https://github.com/servo/rust-smallvec/issues/148
- https://github.com/servo/rust-smallvec/issues/149
- https://github.com/servo/rust-smallvec/commit/c20cfa8584e649f00dc0767ab6fad63a3f59a296
- https://github.com/servo/rust-smallvec/commit/f96322b9243405cc82701cc73f1b19313b413ab4
- https://github.com/servo/rust-smallvec
- https://rustsec.org/advisories/RUSTSEC-2019-0009.html
