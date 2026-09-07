# [C] Langflow CORS misconfiguration enables Account Takeover and RCE

## Summary
Severity: Critical
Advisory: GHSA-577h-p2hh-v4mv
CVE: CVE-2025-34291
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-06
Source: https://github.com/advisories/GHSA-577h-p2hh-v4mv
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.7.0

## Details
Langflow versions up to and including 1.6.9 contain a chained vulnerability that enables account takeover and remote code execution. An overly permissive CORS configuration (allow_origins='*' with allow_credentials=True) combined with a refresh token cookie configured as SameSite=None allows a malicious webpage to perform cross-origin requests that include credentials and successfully call the refresh endpoint. An attacker-controlled origin can therefore obtain fresh access_token / refresh_token pairs for a victim session. Obtained tokens permit access to authenticated endpoints — including built-in code-execution functionality — allowing the attacker to execute arbitrary code and achieve full system compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34291
- https://github.com/langflow-ai/langflow/pull/10139
- https://github.com/langflow-ai/langflow/pull/10696
- https://github.com/langflow-ai/langflow/pull/9240
- https://github.com/langflow-ai/langflow/pull/9441
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2025-78.yaml
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-34291
- https://www.crowdsec.net/vulntracking-report/cve-2025-34291
- https://www.obsidiansecurity.com/blog/cve-2025-34291-critical-account-takeover-and-rce-vulnerability-in-the-langflow-ai-agent-workflow-platform
- https://www.vulncheck.com/advisories/langflow-cors-misconfiguration-to-token-hijack-and-rce
