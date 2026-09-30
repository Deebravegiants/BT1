# [H] PostHog Plugin Server SQL Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-v64v-fq96-c5wv
CVE: CVE-2025-1520
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.0/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-23
Source: https://github.com/advisories/GHSA-v64v-fq96-c5wv
Type: github-advisory

## Affected
- npm: `@posthog/plugin-server` — affected >=0

## Details
PostHog ClickHouse Table Functions SQL Injection Remote Code Execution Vulnerability. This vulnerability allows network-adjacent attackers to execute arbitrary code on affected installations of PostHog. Authentication is required to exploit this vulnerability.

The specific flaw exists within the implementation of the SQL parser. The issue results from the lack of proper validation of a user-supplied string before using it to construct SQL queries. An attacker can leverage this vulnerability to execute code in the context of the database account. Was ZDI-CAN-25350.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1520
- https://github.com/PostHog/posthog/commit/6e8f035f9acd339c5ba87ba6ea40fc1ab3053d42
- https://github.com/PostHog/plugin-server
- https://www.zerodayinitiative.com/advisories/ZDI-25-099
