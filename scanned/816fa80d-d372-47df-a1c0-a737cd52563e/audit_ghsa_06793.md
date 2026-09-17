# [M] Open Babel has NULL pointer dereference in CACAO CacaoFormat::SetHilderbrandt

## Summary
Severity: Medium
Advisory: GHSA-55j6-rjhx-hwfh
CVE: CVE-2025-10999
CWE: CWE-404, CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-55j6-rjhx-hwfh
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's CACAO parser caused a
NULL pointer dereference when reading a crafted input file.

### Details

The flaw was in `CacaoFormat::SetHilderbrandt`. A malformed input
caused the parser to dereference a NULL pointer while applying the
Hilderbrandt transformation.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious CACAO file with the `obabel`
tool, the `OBConversion` API, or any of the language bindings (Python,
Ruby, Java, R, Perl, C#, PHP).

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/ecaed96f
Originally reported as #2827; fixes consolidated in #2913.

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported via OSS-Fuzz.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-55j6-rjhx-hwfh
- https://nvd.nist.gov/vuln/detail/CVE-2025-10999
- https://github.com/openbabel/openbabel/issues/2827
- https://github.com/openbabel/openbabel/commit/ecaed96f
- https://github.com/openbabel/openbabel
- https://github.com/user-attachments/files/22318503/poc.zip
- https://vuldb.com/?ctiid.325927
- https://vuldb.com/?id.325927
- https://vuldb.com/?submit.654064
