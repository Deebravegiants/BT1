# [H] Chainlit contain a server-side request forgery (SSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-2g59-m95p-pgfq
CVE: CVE-2026-22219
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-2g59-m95p-pgfq
Type: github-advisory

## Affected
- PyPI: `chainlit` — affected >=0 <2.9.4

## Details
Chainlit versions prior to 2.9.4 contain a server-side request forgery (SSRF) vulnerability in the /project/element update flow when configured with the SQLAlchemy data layer backend. An authenticated client can provide a user-controlled url value in an Element, which is fetched by the SQLAlchemy element creation logic using an outbound HTTP GET request. This allows an attacker to make arbitrary HTTP requests from the Chainlit server to internal network services or cloud metadata endpoints and store the retrieved responses via the configured storage provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22219
- https://github.com/Chainlit/chainlit/commit/ffc3cce648b343b933e10e85ee5805c7e02ab3bf
- https://github.com/Chainlit/chainlit
- https://github.com/Chainlit/chainlit/releases/tag/2.9.4
- https://www.vulncheck.com/advisories/chainlit-sqlalchemy-data-layer-ssrf-via-project-element
- https://www.zafran.io/resources/chainleak-critical-ai-framework-vulnerabilities-expose-data-enable-cloud-takeover
