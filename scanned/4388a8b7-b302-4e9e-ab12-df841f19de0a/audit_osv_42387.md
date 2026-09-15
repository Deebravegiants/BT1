# [H] Emlog Pro 2.6.23 TLS Certificate Validation Disabled in ai.php

## Summary
Severity: High
Advisory: CVE-2026-67598
Aliases: GHSA-hf85-99vj-m4c5
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-67598
Type: osv

## Details
Emlog Pro through 2.6.23 contains a disabled TLS certificate validation vulnerability in include/service/ai.php that allows network-adjacent attackers to intercept outbound HTTPS requests to configured LLM providers by presenting arbitrary TLS certificates, as CURLOPT_SSL_VERIFYPEER and CURLOPT_SSL_VERIFYHOST are unconditionally disabled across sendStream(), sendImageRequest(), send(), and fetchSearchHtml() with no option to re-enable verification. Attackers can perform man-in-the-middle interception to extract Authorization Bearer API keys from every AI request and inject crafted AI responses that may be acted upon by the tool-call execution pipeline, including the query_database and update_config tool handlers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67598.json
- https://github.com/emlog/emlog/security/advisories/GHSA-hf85-99vj-m4c5
- https://nvd.nist.gov/vuln/detail/CVE-2026-67598
- https://www.vulncheck.com/advisories/emlog-pro-tls-certificate-validation-disabled-in-ai-php
- https://github.com/emlog/emlog
