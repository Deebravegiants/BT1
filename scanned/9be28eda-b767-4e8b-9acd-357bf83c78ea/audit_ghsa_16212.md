# [H] pqc_kyber KyberSlash: division timings depending on secrets

## Summary
Severity: High
Advisory: GHSA-x5j2-g63m-f8g4
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-x5j2-g63m-f8g4
Type: github-advisory

## Affected
- crates.io: `pqc_kyber` — affected >=0

## Details
Various Kyber software libraries in various environments leak secret information into timing, specifically because

 * these libraries include a line of code that divides a secret numerator by a public denominator,
 * the number of CPU cycles for division in various environments varies depending on the inputs to the division, and
 * this variation appears within the range of numerators used in these libraries.

The KyberSlash pages track which Kyber [libraries](https://kyberslash.cr.yp.to/libraries.html) have this issue, and include a [FAQ](https://kyberslash.cr.yp.to/faq.html) about the issue.

## Author

The KyberSlash pages were written by Daniel J. Bernstein. The FAQ originally said "I", but some people seemed to have trouble finding this authorship statement, so the FAQ now says "Bernstein" instead.

## URL

The permanent link for the KyberSlash pages is [https://kyberslash.cr.yp.to](https://kyberslash.cr.yp.to).

## Mitigation status in pqc_kyber crate

The issues has not been resolved in the `pqc_kyber` crate. A third-party fork that mitigates this attack vector has been published as [`safe_pqc_kyber`](https://crates.io/crates/safe_pqc_kyber).

## References
- https://github.com/Argyle-Software/kyber/issues/108
- https://github.com/bwesterb/argyle-kyber/commit/b5c6ad13f4eece80e59c6ebeafd787ba1519f5f6
- https://github.com/Argyle-Software/kyber
- https://rustsec.org/advisories/RUSTSEC-2023-0079.html
