# [H] Open Babel has uninitialized pointer dereference in GRO residue parser

## Summary
Severity: High
Advisory: GHSA-mw5r-wq2m-397c
CVE: CVE-2022-42885
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-mw5r-wq2m-397c
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's GRO parser caused an
uninitialized pointer dereference when reading a crafted input file.

### Details

The flaw was in the residue handling of the GRO reader. A malformed
record caused the parser to use a residue pointer that had never been
initialized.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious GRO file with the `obabel`
tool, the `OBConversion` API, or any of the language bindings (Python,
Ruby, Java, R, Perl, C#, PHP).

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/fa9a2d9a

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported by Cisco TALOS.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-mw5r-wq2m-397c
- https://nvd.nist.gov/vuln/detail/CVE-2022-42885
- https://github.com/openbabel/openbabel/commit/fa9a2d9a2eb75154b7a884dfe679ff41a8f9c547
- https://github.com/openbabel/openbabel
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1668
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1668
