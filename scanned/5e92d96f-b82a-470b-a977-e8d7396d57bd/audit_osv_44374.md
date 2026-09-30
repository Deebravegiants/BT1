# [C] openssl_encrypt before 1.4.9 Plugin Signing Trust Anchor Enrollment Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-81714
Aliases: GHSA-xg52-638v-jc5m, PYSEC-2026-3799
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81714
Type: osv

## Details
openssl_encrypt (pip: openssl-encrypt) versions <= 1.4.8 use suffix-tolerant fingerprint matching in enroll_trust_key when binding a plugin-signing trust anchor. An operator who confirms a short (forgeable, ~32-bit) GPG key id could unknowingly enroll an attacker's colliding key as a trusted anchor, which then vouches for malicious plugins under the ENFORCE signature policy. Version 1.4.9 fixes this by requiring the confirmed value to exactly match the full primary-key fingerprint (case-insensitive, whitespace-stripped).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81714.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-xg52-638v-jc5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-81714
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-plugin-signing-trust-anchor-enrollment-bypass
