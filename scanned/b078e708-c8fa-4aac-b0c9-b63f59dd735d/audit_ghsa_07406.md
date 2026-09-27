# [H] Open Babel has out-of-bounds write in CSR PadString (title field)

## Summary
Severity: High
Advisory: GHSA-p594-7xw4-g76p
CVE: CVE-2022-41793
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-p594-7xw4-g76p
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's CSR parser allowed an
out-of-bounds write when reading a crafted input file.

### Details

The flaw was in the `PadString` helper used to handle the CSR title
field. A title longer than the fixed destination buffer caused the
parser to write past the end of the buffer.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to open a malicious CSR file with the `obabel`
tool, the `OBConversion` API, or any of the language bindings (Python,
Ruby, Java, R, Perl, C#, PHP).

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
- https://github.com/openbabel/openbabel/security/advisories/GHSA-p594-7xw4-g76p
- https://nvd.nist.gov/vuln/detail/CVE-2022-41793
- https://github.com/openbabel/openbabel/commit/528c142f3ad1e3036fc464944f31a23a960cdc3f
- https://github.com/openbabel/openbabel
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1667
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2022-1667
