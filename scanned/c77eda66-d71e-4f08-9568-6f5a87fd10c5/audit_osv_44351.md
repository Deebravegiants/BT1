# [M] openssl_encrypt before 1.4.9 Information Disclosure via Command Line

## Summary
Severity: Medium
Advisory: CVE-2026-81684
Aliases: GHSA-rx2c-m92f-qv6p, PYSEC-2026-3958
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81684
Type: osv

## Details
In openssl_encrypt (pip package openssl-encrypt) versions <= 1.4.8, the desktop GUI passes the steganography password to the CLI child process on the command line via the --stego-password argument (on both encrypt and decrypt paths) instead of via an environment variable as done for the main password. Any local user can read the steganography password from /proc/<pid>/cmdline for the lifetime of the subprocess. Fixed in 1.4.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81684.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-rx2c-m92f-qv6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-81684
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-information-disclosure-via-command-line
