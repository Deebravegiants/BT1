# [H] Open Babel has uninitialized pointer dereference in PQS pFormat

## Summary
Severity: High
Advisory: GHSA-8qxc-57hf-hc9j
CVE: CVE-2022-46280
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-8qxc-57hf-hc9j
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's PQS parser caused an
uninitialized pointer dereference when reading a crafted input file.

### Details

The flaw was in the `pFormat` handling of the PQS reader. A malformed
input caused the parser to dereference a format pointer that had
never been initialized.

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
- https://github.com/openbabel/openbabel/security/advisories/GHSA-8qxc-57hf-hc9j
- https://nvd.nist.gov/vuln/detail/CVE-2022-46280
- https://github.com/openbabel/openbabel/commit/2a7d2cda8bd47daade2e555e34b69651a2e132ef
- https://github.com/openbabel/openbabel
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1670
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1670
