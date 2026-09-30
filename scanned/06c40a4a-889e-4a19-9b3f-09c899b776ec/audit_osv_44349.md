# [C] openssl_encrypt before 1.4.9 Insecure File Permissions

## Summary
Severity: Critical
Advisory: CVE-2026-81682
Aliases: GHSA-7q4g-rrw4-rf2m
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81682
Type: osv

## Details
openssl_encrypt versions before 1.4.9 contain an insecure file permissions vulnerability in the desktop GUI that writes decrypted plaintext with world-readable default permissions. Attackers can read decrypted output files created by the GUI as unprivileged local users on multi-user systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81682.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-7q4g-rrw4-rf2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-81682
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-insecure-file-permissions
