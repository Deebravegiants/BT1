# [H] rsync < 3.5.0 TLS Certificate Validation Bypass via SSL/OpenSSL Mode

## Summary
Severity: High
Advisory: CVE-2026-70454
Aliases: GHSA-3c3x-ww2w-5r5p
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70454
Type: osv

## Details
rsync 3.2.0 through 3.2.3 (openssl mode) and rsync-ssl through 3.4.4 (stunnel mode) contain a TLS certificate validation vulnerability that allows on-path attackers to intercept encrypted sessions by presenting self-signed or otherwise invalid certificates. Attackers can exploit the failure to validate server TLS certificates against a trusted CA or verify certificate hostname matching to decrypt or tamper with rsync session content without detection by the client.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70454.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-3c3x-ww2w-5r5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-70454
- https://www.vulncheck.com/advisories/rsync-tls-certificate-validation-bypass-via-ssl-openssl-mode
- https://github.com/RsyncProject/rsync
