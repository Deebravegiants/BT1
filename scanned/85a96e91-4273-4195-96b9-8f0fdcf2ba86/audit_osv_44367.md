# [C] openssl_encrypt before 1.4.9 Arbitrary Code Execution via unsigned plugin

## Summary
Severity: Critical
Advisory: CVE-2026-81701
Aliases: GHSA-wxx9-p55f-wm34, PYSEC-2026-3778
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81701
Type: osv

## Details
openssl_encrypt versions before 1.4.9 use a denylist to identify trusted built-in plugins, allowing unsigned plugins in top-level plugins/ directories and unknown subdirectories to bypass signature verification. Attackers can place malicious unsigned plugins following documented installation paths to achieve arbitrary code execution in the CLI process with access to passwords and cryptographic keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81701.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-wxx9-p55f-wm34
- https://nvd.nist.gov/vuln/detail/CVE-2026-81701
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-arbitrary-code-execution-via-unsigned-plugin
