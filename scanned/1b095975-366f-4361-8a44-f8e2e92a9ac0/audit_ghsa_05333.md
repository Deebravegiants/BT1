# [H] Prefect has an Authentication Middleware Bypass when URL paths are appended with 'health' or 'ready'

## Summary
Severity: High
Advisory: GHSA-c635-393c-hcx2
CVE: CVE-2026-3514
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-02
Source: https://github.com/advisories/GHSA-c635-393c-hcx2
Type: github-advisory

## Affected
- PyPI: `prefect` — affected >=0 <3.6.22.dev7

## Details
In version 3.6.19 of prefecthq/prefect, an authentication bypass vulnerability exists due to the improper handling of URL path exemptions for health check probes. Specifically, the authentication middleware exempts any URL path ending with 'health' or 'ready' from authentication checks. This allows an attacker to create resources with names ending in 'health' or 'ready' and access them without authentication. Affected endpoints include those for variables, flows, work pools, work queues, and deployments. This vulnerability can lead to unauthorized access to sensitive information, such as API keys and database credentials, stored in Prefect Variables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3514
- https://github.com/prefecthq/prefect/commit/e21617125335025b4b27e7d6f0ca028e8e8f3b79
- https://github.com/PrefectHQ/prefect
- https://huntr.com/bounties/c540e5e1-f74f-44f4-bfa0-9764ff6daa75
