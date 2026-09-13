# [M] openssl_encrypt before 1.4.9 KDF Downgrade via CWD-relative Configuration

## Summary
Severity: Medium
Advisory: CVE-2026-81697
Aliases: GHSA-7j2v-g84w-m75v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81697
Type: osv

## Details
openssl_encrypt (pip package openssl-encrypt) versions <= 1.4.8 contain a CWD-relative configuration file resolution flaw in crypt_settings.py, where CONFIG_FILE (originally the absolute per-user path ~/.crypt_settings.json) is reassigned at line 84 to the bare relative name 'crypt_settings.json'. As a result, the legacy Tk GUI's SettingsTab reads and writes KDF settings from crypt_settings.json in the process launch (current working) directory instead of the user's home directory. An attacker who plants a malicious crypt_settings.json (e.g. sha256:1 with all memory-hard KDFs disabled) can silently downgrade encryption performed in that GUI session to roughly one hash round, bypassing the weak-KDF preflight and enabling offline brute-force attacks against the resulting ciphertext. Fixed in 1.4.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81697.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-7j2v-g84w-m75v
- https://nvd.nist.gov/vuln/detail/CVE-2026-81697
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-kdf-downgrade-via-cwd-relative-configuration
