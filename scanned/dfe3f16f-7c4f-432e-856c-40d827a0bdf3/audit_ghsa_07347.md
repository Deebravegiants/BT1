# [M] Open Babel has out-of-bounds read in PQS lowerit (pre-buffer read)

## Summary
Severity: Medium
Advisory: GHSA-m982-7q3h-r784
CVE: CVE-2025-11000
CWE: CWE-125, CWE-404
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-m982-7q3h-r784
Type: github-advisory

## Affected
- PyPI: `openbabel` — affected >=0 <3.2.0

## Details
### Summary

A memory-safety vulnerability in Open Babel's PQS parser caused an
out-of-bounds (pre-buffer) read when reading a crafted input file.

### Details

The flaw was in the `lowerit` helper used by the PQS parser. A
malformed input caused the helper to read one or more bytes before
the start of its input buffer.

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

Fix commit: https://github.com/openbabel/openbabel/commit/f4a5ebae
Fixes consolidated in #2913.

A minimized reproducer for this CVE is checked in under
`test/files/fuzz_regress/` and is exercised on every CI build under
ASAN+UBSAN by the `fuzzregresstest` harness.

### Credit

Reported via OSS-Fuzz.

## References
- https://github.com/openbabel/openbabel/security/advisories/GHSA-m982-7q3h-r784
- https://nvd.nist.gov/vuln/detail/CVE-2025-11000
- https://github.com/openbabel/openbabel/issues/2826
- https://github.com/openbabel/openbabel/commit/f4a5ebae
- https://github.com/openbabel/openbabel
- https://github.com/user-attachments/files/22318474/poc.zip
- https://vuldb.com/?ctiid.325928
- https://vuldb.com/?id.325928
- https://vuldb.com/?submit.654066
