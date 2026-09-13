# [H] Use after free in string-interner

## Summary
Severity: High
Advisory: GHSA-49fq-pw77-6qxj
CVE: CVE-2019-16882
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-49fq-pw77-6qxj
Type: github-advisory

## Affected
- crates.io: `string-interner` — affected >=0.7.0 <0.7.1
- crates.io: `string-interner` — affected >=0 <0.6.4

## Details
Affected versions of this crate did not clone contained strings when an interner is cloned. Interners have raw pointers to the contained strings, and they keep pointing the strings which the old interner owns, after the interner is cloned. If a new cloned interner is alive and the old original interner is dead, the new interner has dangling pointers to the old interner's storage, which is already dropped.

This allows an attacker to read the already freed memory. The dangling pointers are used by the interners to check a string is already interned. An attacker can do brute force attack to get the data pointed by the dangling pointer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16882
- https://github.com/Robbepop/string-interner/issues/9
- https://github.com/Robbepop/string-interner/pull/10
- https://github.com/Robbepop/string-interner/commit/d91dac0cfe42512526879cdfaac0b81beff54089
- https://github.com/Robbepop/string-interner
- https://rustsec.org/advisories/RUSTSEC-2019-0023.html
