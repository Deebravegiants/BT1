# [H] OpenReplay: Cross-tenant information disclosure in app_apikey projectKey routes via missing tenant binding

## Summary
Severity: High
Advisory: CVE-2026-45296
Aliases: GHSA-8wmc-vpmf-cjf5
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-45296
Type: osv

## Details
OpenReplay is a self-hosted session replay suite. Prior to 1.26.0, OpenReplay's Python API exposes several app_apikey routes that trust a caller-provided projectKey after validating only that the API key itself is valid and that the target projectKey exists. The authorization flow does not verify that the authenticated API key and the requested project belong to the same tenant. Because the public tracker design exposes projectKey to browser-side code, an attacker who owns any valid API key for their own tenant can target another tenant's project by reusing that public projectKey. The vulnerable routes allow the attacker to enumerate victim user sessions and then retrieve sensitive session event data across the tenant boundary. This vulnerability is fixed in 1.26.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45296.json
- https://github.com/openreplay/openreplay/security/advisories/GHSA-8wmc-vpmf-cjf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45296
