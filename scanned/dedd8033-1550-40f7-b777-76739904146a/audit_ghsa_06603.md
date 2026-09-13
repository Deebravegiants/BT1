# [H] Open Babel has out-of-bounds write in MOPAC IN translationVectors[] (Tv atom)

## Summary
Severity: High
Advisory: GHSA-mjmg-352j-f456
CVE: CVE-2022-46294
CWE: CWE-119, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-mjmg-352j-f456
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's MOPAC input parser
allowed an out-of-bounds write into the `translationVectors[]` array
when reading Tv (translation-vector) atoms from a crafted input
file.

### Details

The MOPAC IN reader stored Tv-atom translation vectors into a
fixed-size `translationVectors[]` array. A malformed input with
more than three Tv atoms (or three plus extras) could push more
vectors than the array had slots, causing a write past the end of
the array. One of five `translationVectors[]` OOB writes in the
TALOS 2022 batch.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious MOPAC input file with the
`obabel` tool, the `OBConversion` API, or any of the language
bindings (Python, Ruby, Java, R, Perl, C#, PHP).

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/40e85213

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported by Cisco TALOS.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-mjmg-352j-f456
- https://nvd.nist.gov/vuln/detail/CVE-2022-46294
- https://github.com/openbabel/openbabel/commit/40e852138f21d586b7ccdce6329e7b23a87168bb
- https://github.com/openbabel/openbabel
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1666
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1666
