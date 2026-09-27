# [M] Sequoia PGP has Subtraction Overflow when aes_key_unwrap function is provided ciphertext that is too short

## Summary
Severity: Medium
Advisory: GHSA-v6x3-9r38-r27q
CVE: CVE-2025-67897
CWE: CWE-195
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-14
Source: https://github.com/advisories/GHSA-v6x3-9r38-r27q
Type: github-advisory

## Affected
- crates.io: `sequoia-openpgp` — affected >=0 <2.1.0

## Details
In Sequoia before 2.1.0, aes_key_unwrap panics if passed a ciphertext that is too short. A remote attacker can take advantage of this issue to crash an application by sending a victim an encrypted message with a crafted PKESK or SKESK packet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67897
- https://bugs.debian.org/1122582
- https://gitlab.com/sequoia-pgp/sequoia
- https://gitlab.com/sequoia-pgp/sequoia/-/blob/b59886e5e7bdf7169ed330f309a6633d131776e5/openpgp/NEWS#L7-L26
- https://gitlab.com/sequoia-pgp/sequoia/-/commit/b59886e5e7bdf7169ed330f309a6633d131776e5
- https://rustsec.org/advisories/RUSTSEC-2025-0136.html
