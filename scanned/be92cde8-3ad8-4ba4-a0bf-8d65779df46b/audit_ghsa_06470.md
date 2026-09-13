# [H] Open Babel has out-of-bounds write in PQS coord_file parser

## Summary
Severity: High
Advisory: GHSA-f29h-2h58-48r7
CVE: CVE-2022-43467
CWE: CWE-119, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-f29h-2h58-48r7
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's PQS parser allowed an
out-of-bounds write when reading a crafted input file.

### Details

The flaw was in the `coord_file` parsing path of the PQS reader. A
malformed coord file specifier caused the parser to write past the
end of its destination buffer.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious PQS file with the `obabel`
tool, the `OBConversion` API, or any of the language bindings (Python,
Ruby, Java, R, Perl, C#, PHP).

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/2a7d2cda

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported by Cisco TALOS.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-f29h-2h58-48r7
- https://nvd.nist.gov/vuln/detail/CVE-2022-43467
- https://github.com/openbabel/openbabel/commit/2a7d2cda8bd47daade2e555e34b69651a2e132ef
- https://github.com/openbabel/openbabel
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1671
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1671
