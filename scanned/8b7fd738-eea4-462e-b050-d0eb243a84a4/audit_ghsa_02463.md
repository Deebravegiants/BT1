# [C] Out of bounds access in lucet-runtime-internals

## Summary
Severity: Critical
Advisory: GHSA-3933-wvjf-pcvc
CVE: CVE-2020-35859
CWE: CWE-125, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3933-wvjf-pcvc
Type: github-advisory

## Affected
- crates.io: `lucet-runtime-internals` — affected >=0 <0.4.3
- crates.io: `lucet-runtime-internals` — affected >=0.5.0 <0.5.1

## Details
An embedding using affected versions of lucet-runtime configured to use non-default Wasm globals sizes of more than 4KiB, or compiled in debug mode without optimizations, could leak data from the signal handler stack to guest programs. This can potentially cause data from the embedding host to leak to guest programs or cause corruption of guest program memory. This flaw was resolved by correcting the sigstack allocation logic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35859
- https://github.com/bytecodealliance/lucet/pull/401
- https://github.com/fastly/lucet
- https://rustsec.org/advisories/RUSTSEC-2020-0004.html
