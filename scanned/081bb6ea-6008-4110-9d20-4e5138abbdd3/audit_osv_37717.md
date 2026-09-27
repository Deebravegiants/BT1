# [M] SQLBot: SSRF to Arbitrary File Read (AFR) via Rogue MySQL

## Summary
Severity: Medium
Advisory: CVE-2026-32949
Aliases: GHSA-wqj3-xcxf-j9m9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32949
Type: osv

## Details
SQLBot is an intelligent data query system based on a large language model and RAG. Versions prior to 1.7.0 contain a Server-Side Request Forgery (SSRF) vulnerability that allows an attacker to retrieve arbitrary system and application files from the server. An attacker can exploit the /api/v1/datasource/check endpoint by configuring a forged MySQL data source with a malicious parameter extraJdbc="local_infile=1". When the SQLBot backend attempts to verify the connectivity of this data source, an attacker-controlled Rogue MySQL server issues a malicious LOAD DATA LOCAL INFILE command during the MySQL handshake. This forces the target server to read arbitrary files from its local filesystem (such as /etc/passwd or configuration files) and transmit the contents back to the attacker. This issue was fixed in version 1.7.0.

## References
- https://github.com/dataease/SQLBot/releases/tag/v1.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32949.json
- https://github.com/dataease/SQLBot/security/advisories/GHSA-wqj3-xcxf-j9m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32949
- https://github.com/dataease/SQLBot/commit/ff98514827bad99b8fa4b39385adecc6e3d44355
