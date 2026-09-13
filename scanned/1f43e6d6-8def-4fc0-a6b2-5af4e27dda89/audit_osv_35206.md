# [C] LibreChat is vulnerable to Server-Side Request Forgery due to missing restrictions

## Summary
Severity: Critical
Advisory: CVE-2025-69222
Aliases: GHSA-rgjq-4q58-m3q8
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-69222
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Version 0.8.1-rc2 is prone to a server-side request forgery (SSRF)
vulnerability due to missing restrictions of the Actions feature in the default configuration. LibreChat enables users to configure agents with predefined instructions and actions that can interact with remote services via OpenAPI specifications, supporting various HTTP methods, parameters, and authentication methods including custom headers. By default, there are no restrictions on accessible services, which means agents can also access internal components like the RAG API included in the default Docker Compose setup. This issue is fixed in version 0.8.1-rc2.

## References
- https://github.com/danny-avila/LibreChat/releases/tag/v0.8.2-rc2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69222.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-rgjq-4q58-m3q8
- https://nvd.nist.gov/vuln/detail/CVE-2025-69222
- https://github.com/danny-avila/LibreChat/commit/3b41e392ba5c0d603c1737d8582875e04eaa6e02
