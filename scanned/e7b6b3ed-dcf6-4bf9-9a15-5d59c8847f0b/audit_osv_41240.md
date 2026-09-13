# [H] Cognee < 1.2.0 Unauthorized LLM Configuration Overwrite via /api/v1/settings

## Summary
Severity: High
Advisory: CVE-2026-58473
Aliases: GHSA-49f7-whx5-4256, PYSEC-2026-3816
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-58473
Type: osv

## Details
Cognee before 1.2.0 contains an improper access control vulnerability that allows unauthenticated attackers to overwrite the global LLM provider configuration by self-registering an account and calling the settings endpoint, which performs no admin or superuser check. Attackers can redirect all LLM operations instance-wide to an attacker-controlled endpoint by exploiting the process-wide singleton configuration cache, enabling exfiltration of prompts, uploaded documents, extracted entities, and knowledge graph content from all users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58473.json
- https://github.com/topoteretes/cognee/releases/tag/v1.2.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-58473
- https://www.vulncheck.com/advisories/cognee-unauthorized-llm-configuration-overwrite-via-api-v1-settings
- https://github.com/topoteretes/cognee/commit/d10b1b77e2157c6238fd4d1acb1923a048991699
- https://github.com/topoteretes/cognee
- https://github.com/topoteretes/cognee/issues/3084
