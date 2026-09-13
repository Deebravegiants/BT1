# [C] SPIP < 4.4.9 Insecure Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-27475
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2026-27475
Type: osv

## Details
SPIP before 4.4.9 allows Insecure Deserialization in the public area through the table_valeur filter and the DATA iterator, which accept serialized data. An attacker who can place malicious serialized content (a pre-condition requiring prior access or another vulnerability) can trigger arbitrary object instantiation and potentially achieve code execution. The use of serialized data in these components has been deprecated and will be removed in SPIP 5. This vulnerability is not mitigated by the SPIP security screen.

## References
- https://git.spip.net/spip/spip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27475.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27475
- https://www.vulncheck.com/advisories/spip-insecure-deserialization
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-4-9.html
