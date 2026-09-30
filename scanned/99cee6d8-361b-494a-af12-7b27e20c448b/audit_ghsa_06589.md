# [H] Open Babel has heap buffer overflow in ChemKin ChemKinFormat::CheckSpecies

## Summary
Severity: High
Advisory: GHSA-8wq6-qh76-wpv9
CVE: CVE-2025-10997
CWE: CWE-119, CWE-122
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-8wq6-qh76-wpv9
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's ChemKin parser caused
a heap buffer overflow when reading a crafted input file.

### Details

The flaw was in `ChemKinFormat::CheckSpecies`. A malformed species
record caused the parser to write past the end of a heap-allocated
buffer.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious ChemKin file with the
`obabel` tool, the `OBConversion` API, or any of the language
bindings (Python, Ruby, Java, R, Perl, C#, PHP).

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/af4a4212
Originally reported as #2830; fixes consolidated in #2913.

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported via OSS-Fuzz.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-8wq6-qh76-wpv9
- https://nvd.nist.gov/vuln/detail/CVE-2025-10997
- https://github.com/openbabel/openbabel/issues/2830
- https://github.com/openbabel/openbabel
- https://github.com/user-attachments/files/22318543/poc.zip
- https://vuldb.com/?ctiid.325925
- https://vuldb.com/?id.325925
- https://vuldb.com/?submit.654062
