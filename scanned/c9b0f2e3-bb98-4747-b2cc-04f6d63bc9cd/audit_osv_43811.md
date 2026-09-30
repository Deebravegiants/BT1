# [M] openssl_encrypt before 1.4.0 Insecure Default Configuration

## Summary
Severity: Medium
Advisory: CVE-2026-74882
Aliases: GHSA-2592-7m3g-7fq6, PYSEC-2026-3744
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74882
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain an insecure default configuration that trusts the entire RFC 1918 private address space in IntegrityProxyConfig trusted_proxies. Attackers on private networks can forge client certificate headers to bypass mTLS authentication when ProxyAuth validation is relaxed or modified.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74882.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-2592-7m3g-7fq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-74882
- https://www.vulncheck.com/advisories/openssl-encrypt-before-insecure-default-configuration
