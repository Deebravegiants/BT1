# [H] Flaw in streaming state in orion

## Summary
Severity: High
Advisory: GHSA-gffv-5hr2-f9gj
CVE: CVE-2018-20999
CWE: CWE-682
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gffv-5hr2-f9gj
Type: github-advisory

## Affected
- crates.io: `orion` — affected >=0 <0.11.2

## Details
Affected versions of this crate did not properly reset a streaming state. Resetting a streaming state, without finalising it first, creates incorrect results. The flaw was corrected by not first checking if the state had already been reset, when calling reset().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20999
- https://github.com/brycx/orion/issues/46
- https://github.com/brycx/orion
- https://rustsec.org/advisories/RUSTSEC-2018-0012.html
