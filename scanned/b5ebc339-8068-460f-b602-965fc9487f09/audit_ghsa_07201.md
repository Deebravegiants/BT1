# [H] Open Babel has out-of-bounds write in ORCA nAtoms parser (second variant)

## Summary
Severity: High
Advisory: GHSA-5rff-8f7c-8jmw
CVE: CVE-2022-46290
CWE: CWE-122, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-5rff-8f7c-8jmw
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's ORCA parser allowed an
out-of-bounds write when reading a crafted input file.

### Details

A second variant of the `nAtoms` out-of-bounds write in the ORCA
reader: a different malformed-input path produced the same class of
write past the end of the destination buffer.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious ORCA file with the `obabel`
tool, the `OBConversion` API, or any of the language bindings (Python,
Ruby, Java, R, Perl, C#, PHP).

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/b239d06e

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported by Cisco TALOS.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-5rff-8f7c-8jmw
- https://nvd.nist.gov/vuln/detail/CVE-2022-46290
- https://github.com/openbabel/openbabel/commit/b239d06eb724bb684eea0040e9d87cf07072b081
- https://github.com/openbabel/openbabel
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1665
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1665
