# [M] openssl_encrypt before 1.4.9 Weak Pepper Key Derivation

## Summary
Severity: Medium
Advisory: CVE-2026-81689
Aliases: GHSA-3v63-778v-3mvp, PYSEC-2026-3959
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81689
Type: osv

## Details
openssl_encrypt versions before 1.4.9 derive the remote-pepper wrap key using unsalted HKDF-SHA256 or bare SHA-256 of the password, allowing identical keys across all users and files. Attackers with access to wrapped pepper blobs can precompute a single dictionary table and perform fleet-wide offline password guessing at hardware speed to recover user passwords.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81689.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-3v63-778v-3mvp
- https://nvd.nist.gov/vuln/detail/CVE-2026-81689
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-weak-pepper-key-derivation
