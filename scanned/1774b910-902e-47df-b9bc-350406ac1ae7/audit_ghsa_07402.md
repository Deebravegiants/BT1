# [H] Open Babel has out-of-bounds write in Gaussian coords_type orientation parser

## Summary
Severity: High
Advisory: GHSA-vr3p-gg26-45v9
CVE: CVE-2022-37331
CWE: CWE-119, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-vr3p-gg26-45v9
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's Gaussian output parser
allowed an out-of-bounds write when reading a crafted input file.

### Details

The flaw was in the `coords_type` orientation parser inside the
Gaussian output reader. A malformed orientation block caused the
parser to write past the end of its destination buffer.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious Gaussian output file with the
`obabel` tool, the `OBConversion` API, or any of the language
bindings (Python, Ruby, Java, R, Perl, C#, PHP).

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/528c142f

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported by Cisco TALOS.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-vr3p-gg26-45v9
- https://nvd.nist.gov/vuln/detail/CVE-2022-37331
- https://github.com/openbabel/openbabel/commit/528c142f
- https://github.com/openbabel/openbabel
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1672
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1672
