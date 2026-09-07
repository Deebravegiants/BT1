# [M] composio Server-Side Request Forgery (SSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qvg9-vp87-h3hr
CVE: CVE-2024-8952
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-qvg9-vp87-h3hr
Type: github-advisory

## Affected
- PyPI: `composio-core` — affected >=0

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in composiohq/composio version v0.4.2, specifically in the /api/actions/execute/WEBTOOL_SCRAPE_WEBSITE_CONTENT endpoint. This vulnerability allows an attacker to read files, access AWS metadata, and interact with local services on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8952
- https://github.com/ComposioHQ/composio
- https://huntr.com/bounties/d1acdd38-10d7-45df-9df0-9fc71f0e1c2a
