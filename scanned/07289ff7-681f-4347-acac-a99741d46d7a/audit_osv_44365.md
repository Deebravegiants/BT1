# [C] openssl_encrypt before 1.4.9 Shell Injection via info command

## Summary
Severity: Critical
Advisory: CVE-2026-81698
Aliases: GHSA-gw2m-mj6q-59hc, PYSEC-2026-3776
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81698
Type: osv

## Details
openssl_encrypt versions before 1.4.9 contain a shell injection vulnerability in the info command's reconstructed CLI block that interpolates untrusted metadata fields without quoting. Attackers can craft metadata values like pepper_name containing shell commands that execute when users copy the printed CLI block into a shell.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81698.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-gw2m-mj6q-59hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-81698
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-shell-injection-via-info-command
