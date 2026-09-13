# [C] openssl_encrypt before 1.4.9 GPG Signature Verification Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-81700
Aliases: GHSA-x38r-8wf3-q9hq, PYSEC-2026-3777
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81700
Type: osv

## Details
openssl_encrypt versions before 1.4.9 contain a signature verification vulnerability in gpg_runner.verify_detached that accepts revoked and expired keys by only checking VALIDSIG status without inspecting REVKEYSIG, EXPKEYSIG, or gpg exit codes. Attackers holding compromised-then-revoked signing keys or expired project keys can bypass signature verification to execute malicious plugins in the host process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81700.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-x38r-8wf3-q9hq
- https://nvd.nist.gov/vuln/detail/CVE-2026-81700
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-gpg-signature-verification-bypass
