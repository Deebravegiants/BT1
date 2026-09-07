# [H] Unchecked Return Value to NULL Pointer Dereference in PDFDocumentHandler.cpp

## Summary
Severity: High
Advisory: GHSA-rcrx-fpjp-mfrw
CVE: CVE-2022-39381
CWE: CWE-476, CWE-690
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-02
Source: https://github.com/advisories/GHSA-rcrx-fpjp-mfrw
Type: github-advisory

## Affected
- npm: `muhammara` — affected >=0 <2.6.0
- npm: `hummus` — affected >=0 <1.0.111

## Details
### Impact
The package muhammara before 2.6.0; all versions of package hummus are vulnerable to Denial of Service (DoS) when supplied with a maliciously crafted PDF file to be appended to another.

### Patches
It has been patched in 2.6.0 for muhammara and not at all for hummus

### Workarounds
Do not process files from untrusted sources

### References
PR: https://github.com/julianhille/MuhammaraJS/pull/194
Issue: https://github.com/julianhille/MuhammaraJS/issues/191
Issue in hummus: https://github.com/galkahana/HummusJS/issues/293

### Outline differences to https://nvd.nist.gov/vuln/detail/CVE-2022-25892

The difference is one is in [src/deps/PDFWriter/PDFParser.cpp](https://github.com/julianhille/MuhammaraJS/commit/1890fb555eaf171db79b73fdc3ea543bbd63c002#diff-09ac2c64aeab42b14b2ae7b11a5648314286986f8c8444a5b3739ba7203b1e9b) and the other is [PDFDocumentHandler.cpp](https://github.com/julianhille/MuhammaraJS/pull/194/files#diff-38d338ea4c047fd7dd9a05b5ffe7c964f0fa7e79aff4c307ccee7596457b1ef2) both is a null pointer but for different cases
These are totally diffent issues, one is in reading a pdf the other is in appendending a maliciously crafted one. The function calls are different the versions in which they are solved are diffent.

## References
- https://github.com/julianhille/MuhammaraJS/security/advisories/GHSA-rcrx-fpjp-mfrw
- https://nvd.nist.gov/vuln/detail/CVE-2022-39381
- https://github.com/galkahana/HummusJS/issues/293
- https://github.com/julianhille/MuhammaraJS/issues/191
- https://github.com/julianhille/MuhammaraJS/pull/194
- https://github.com/galkahana/HummusJS/commit/a9bf2520ab5abb69f9328906e406fbebfb36159a
- https://github.com/julianhille/MuhammaraJS
