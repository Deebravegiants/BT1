# [M] Unsafe deserialization of decrypted terms enables node DoS in AshCloak

## Summary
Severity: Medium
Advisory: CVE-2026-81319
Aliases: EEF-CVE-2026-81319, GHSA-rc26-mrm2-6pf9
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-81319
Type: osv

## Details
Deserialization of Untrusted Data vulnerability in ash-project ash_cloak allows an attacker who can influence the bytes of an encrypted column to crash the BEAM node, by triggering unbounded atom creation or a decompression bomb during decryption.

AshCloak.Calculations.Decrypt decodes the decrypted binary with Ash.Helpers.non_executable_binary_to_term/1 without the :safe option, so atoms in the payload are interned during the decode and never garbage collected, and the term format's compressed form is inflated transparently. vault.decrypt!() is the only barrier and stops tampering only for an authenticated cipher. Cloak also ships the unauthenticated AES.CTR, whose ciphertext an attacker who knows their own plaintext can XOR into any same-length payload without the key, so an ordinary read of the forged column reaches the decoder. A few hundred kilobytes of distinct atoms exhausts the atom table, or a small compressed payload inflates to gigabytes.

This issue affects ash_cloak: from 0.1.0 before 0.4.0.

## References
- https://cna.erlef.org/cves/CVE-2026-81319.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-81319
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81319.json
- https://github.com/ash-project/ash_cloak/security/advisories/GHSA-rc26-mrm2-6pf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-81319
- https://github.com/ash-project/ash_cloak/commit/1690f0a436efe3e7c11d70d74ff5a8ac0fdf6608
- https://github.com/ash-project/ash_cloak
