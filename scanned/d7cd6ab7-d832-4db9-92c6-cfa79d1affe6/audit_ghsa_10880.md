# [H] jsrsasign: Missing cryptographic validation during DSA signing enables private key extraction

## Summary
Severity: High
Advisory: GHSA-w8q8-93cx-6h7r
CVE: CVE-2026-4601
CWE: CWE-325
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-w8q8-93cx-6h7r
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <11.1.1

## Details
Versions of the package jsrsasign before 11.1.1 are vulnerable to Missing Cryptographic Step via the KJUR.crypto.DSA.signWithMessageHash process in the DSA signing implementation. An attacker can recover the private key by forcing r or s to be zero, so the library emits an invalid signature without retrying, and then solves for x from the resulting signature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4601
- https://github.com/kjur/jsrsasign/pull/645
- https://github.com/kjur/jsrsasign/commit/0710e392ec35de697ce11e4219c988ba2b5fe0eb
- https://gist.github.com/Kr0emer/93789fe6efe5519db9692d4ad1dad586
- https://github.com/kjur/jsrsasign
- https://security.snyk.io/vuln/SNYK-JS-JSRSASIGN-15370941
