# [H] rPGP Panics on Malformed Untrusted Input

## Summary
Severity: High
Advisory: GHSA-9rmp-2568-59rv
CVE: CVE-2024-53856
CWE: CWE-130, CWE-248, CWE-617
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-9rmp-2568-59rv
Type: github-advisory

## Affected
- crates.io: `pgp` — affected >=0 <0.14.1

## Details
During a security audit, [Radically Open Security](https://www.radicallyopensecurity.com/) discovered several reachable edge cases which allow an attacker to trigger `rpgp` crashes by providing crafted data.

### Impact
When processing malformed input, `rpgp` can run into Rust panics which halt the program.

This can happen in the following scenarios:
* Parsing OpenPGP messages from binary or armor format
* Decrypting OpenPGP messages via `decrypt_with_password()`
* Parsing or converting public keys
* Parsing signed cleartext messages from armor format
* Using malformed private keys to sign or encrypt

Given the affected components, we consider most attack vectors to be reachable by remote attackers during typical use cases of the `rpgp` library. The attack complexity is low since the malformed messages are generic, short, and require no victim-specific knowledge.

The result is a denial-of-service impact via program termination. There is no impact to confidentiality or integrity security properties.

### Versions and Patches
All recent versions are affected by at least some of the above mentioned issues. 

The vulnerabilities have been fixed with version `0.14.1`. We recommend all users to upgrade to this version.

### References


The security audit was made possible by the [NLnet Foundation NGI Zero Core](https://nlnet.nl/core/) grant program [for rpgp](https://nlnet.nl/project/rPGP-cryptorefresh/).

## References
- https://github.com/rpgp/rpgp/security/advisories/GHSA-9rmp-2568-59rv
- https://nvd.nist.gov/vuln/detail/CVE-2024-53856
- https://github.com/rpgp/rpgp
- https://rustsec.org/advisories/RUSTSEC-2024-0447.html
