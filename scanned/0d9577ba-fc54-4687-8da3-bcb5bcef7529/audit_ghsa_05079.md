# [H] Open Babel has heap buffer overflow in SMILES OBSmilesParser::ParseSmiles

## Summary
Severity: High
Advisory: GHSA-j35x-w4gj-pf7w
CVE: CVE-2025-10996
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-j35x-w4gj-pf7w
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's SMILES parser caused a
heap buffer overflow when reading a crafted input string.

### Details

The flaw was in `OBSmilesParser::ParseSmiles`. A malformed SMILES
input caused the parser to write past the end of a heap-allocated
buffer.

### Impact

Open Babel is a C++ library and CLI used to read and write chemistry
file formats; it is shipped by Linux distributions and embedded in
services that may parse untrusted input. Triggering this vulnerability
requires the victim to parse a malicious SMILES string with the
`obabel` tool, the `OBConversion` API, or any of the language
bindings (Python, Ruby, Java, R, Perl, C#, PHP). SMILES strings are
commonly passed on the command line and through scripted pipelines,
so this primitive is especially reachable.

### Affected versions

All releases up to and including 3.1.1.

### Patched version

3.2.0 (released 2026-05-26).

### Patch

Fix commit: https://github.com/openbabel/openbabel/commit/b34cd604
Originally reported as #2831; fixes consolidated in #2913.

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported via OSS-Fuzz.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-j35x-w4gj-pf7w
- https://nvd.nist.gov/vuln/detail/CVE-2025-10996
- https://github.com/openbabel/openbabel/issues/2831
- https://github.com/openbabel/openbabel/pull/2913
- https://github.com/openbabel/openbabel/commit/b34cd604
- https://github.com/openbabel/openbabel
- https://github.com/user-attachments/files/22318556/poc.zip
- https://vuldb.com/?ctiid.325924
- https://vuldb.com/?id.325924
- https://vuldb.com/?submit.654060
