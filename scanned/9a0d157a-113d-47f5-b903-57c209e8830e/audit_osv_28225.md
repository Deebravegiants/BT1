# [M] CVE-2024-29370

## Summary
Severity: Medium
Advisory: CVE-2024-29370
Aliases: GHSA-h4pw-wxh7-4vjj, PYSEC-2025-185
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2024-29370
Type: osv

## Details
In python-jose 3.3.0 (specifically jwe.decrypt), a vulnerability allows an attacker to cause a Denial-of-Service (DoS) condition by crafting a malicious JSON Web Encryption (JWE) token with an exceptionally high compression ratio. When this token is processed by the server, it results in significant memory allocation and processing time during decompression.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29370.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-29370
- https://github.com/mpdavis/python-jose/issues/344
