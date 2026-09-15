# [M] strongMan vulnerable to private credential recovery due to key and counter reuse

## Summary
Severity: Medium
Advisory: CVE-2026-25998
Aliases: GHSA-88w4-jv97-c8xr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-25998
Type: osv

## Details
strongMan is a management interface for strongSwan, an OpenSource IPsec-based VPN. When storing credentials in the database (private keys, EAP secrets), strongMan encrypts the corresponding database fields. So far it used AES in CTR mode with a global database key. Together with an initialization vector (IV), a key stream is generated to encrypt the data in the database fields. But because strongMan did not generate individual IVs, every database field was encrypted using the same key stream. An attacker that has access to the database can use this to recover the encrypted credentials. In particular, because certificates, which have to be considered public information, are also encrypted using the same mechanism, an attacker can directly recover a large chunk of the key stream, which allows them to decrypt basically all other secrets especially ECDSA private keys and EAP secrets, which are usually a lot shorter. Version 0.2.0 fixes the issue by switching to AES-GCM-SIV encryption with a random nonce and an individually derived encryption key, using HKDF, for each encrypted value. Database migrations are provided to automatically re-encrypt all credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25998.json
- https://github.com/strongswan/strongMan/security/advisories/GHSA-88w4-jv97-c8xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25998
