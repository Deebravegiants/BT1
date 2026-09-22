# [M] Ed25519 Signature Malleability in ed25519-java Due to Missing Scalar Range Check

## Summary
Severity: Medium
Advisory: GHSA-p53j-g8pw-4w5f
CVE: CVE-2020-36843
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-13
Source: https://github.com/advisories/GHSA-p53j-g8pw-4w5f
Type: github-advisory

## Affected
- Maven: `net.i2p.crypto:eddsa` — affected >=0
- Maven: `net.i2p:i2p` — affected >=0 <0.9.39

## Details
The implementation of EdDSA in EdDSA-Java (aka ed25519-java) through 0.3.0 exhibits signature malleability and does not satisfy the SUF-CMA (Strong Existential Unforgeability under Chosen Message Attacks) property. This allows attackers to create new valid signatures different from previous signatures for a known message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36843
- https://github.com/str4d/ed25519-java/issues/82#issue-727629226
- https://github.com/i2p/i2p.i2p/commit/d7d1dcb5399c61cf2916ccc45aa25b0209c88712#diff-658f7b1aa34b58d27796fccdb8b756c72702d64ae44703374960f1cb89a5a5c3
- https://eprint.iacr.org/2020/1244
- https://github.com/str4d/ed25519-java
