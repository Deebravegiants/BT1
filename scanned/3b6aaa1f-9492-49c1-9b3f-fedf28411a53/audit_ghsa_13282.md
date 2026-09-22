# [M] libostree vulnerable to denial of service attack

## Summary
Severity: Medium
Advisory: GHSA-x96g-95fq-4xv4
CVE: CVE-2022-47085
Ecosystem: crates.io
Published: 2023-07-18
Source: https://github.com/advisories/GHSA-x96g-95fq-4xv4
Type: github-advisory

## Affected
- crates.io: `ostree` — affected >=0 <0.17.1

## Details
An issue was discovered in ostree before version 0.17.1 allows attackers to cause a denial of service via the print_panic function in repo_checkout_filter.rs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47085
- https://github.com/ostreedev/ostree/issues/2775
- https://github.com/ostreedev/ostree/commit/d9bb160a7c1e7f0a2308a7282622b91bc27d448c
- https://doc.rust-lang.org/std/macro.eprintln.html
- https://github.com/ostreedev/ostree
