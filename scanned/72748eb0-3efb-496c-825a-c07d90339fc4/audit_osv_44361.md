# [C] verify-usb before 1.4.9 Output Injection via Unsanitized Filenames

## Summary
Severity: Critical
Advisory: CVE-2026-81694
Aliases: GHSA-c793-rj9w-r3wg, PYSEC-2026-3960
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81694
Type: osv

## Details
openssl-encrypt (pip package, versions <= 1.4.8) fails to sanitize filenames read from untrusted drive data (outside the AES-GCM authenticated manifest) before printing them in the verify-usb command's output. An attacker can plant filenames containing terminal cursor-movement and erase-line control bytes that repaint a forged PASSED verdict on screen, masking actual tamper detection. Fixed in 1.4.9 by routing drive-derived names through sanitize_for_display().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81694.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-c793-rj9w-r3wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-81694
- https://www.vulncheck.com/advisories/verify-usb-before-1.4.9-output-injection-via-unsanitized-filenames
