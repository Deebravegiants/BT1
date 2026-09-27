# [C] openssl_encrypt before 1.4.0 Weak Shared Secret via PQC Simulation Mode

## Summary
Severity: Critical
Advisory: CVE-2026-74900
Aliases: GHSA-p3gq-pcg9-qvfv, PYSEC-2026-3772
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74900
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain a critical vulnerability in pqc.py where KEM decapsulation failures silently fall back to simulation mode, generating a deterministic shared secret from only 16 bytes of the private key and publicly available encapsulated key data. Attackers who obtain 16 bytes of the private key can compute the shared secret and decrypt all ciphertext, as the fallback triggers on any KEM failure without raising an error.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74900.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-p3gq-pcg9-qvfv
- https://nvd.nist.gov/vuln/detail/CVE-2026-74900
- https://www.vulncheck.com/advisories/openssl-encrypt-before-weak-shared-secret-via-pqc-simulation-mode
