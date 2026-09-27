# [M] Server-Side Request Forgery (SSRF) and Credential Exfiltration in googleapis/mcp-toolbox cloud-healthcare-fhir-fetch-page Tool

## Summary
Severity: Medium
Advisory: CVE-2026-16481
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-16481
Type: osv

## Details
A Server-Side Request Forgery (SSRF) and credential exfiltration vulnerability exists in the cloud-healthcare-fhir-fetch-page tool of googleapis/mcp-toolbox.

The tool takes an unvalidated pageURL parameter from the client and issues an HTTP GET request to it using an authenticated client. The underlying transport automatically attaches an Authorization: Bearer  header to every outbound request regardless of the destination host. An attacker can supply an arbitrary external URL to the pageURL parameter (either directly via the tool execution payload or implicitly via data-driven pagination tracking loops), leading Toolbox into sending its OAuth/service-account access token to an attacker-controlled listener. Depending on the configuration, this leaks either the end-user's token or the broader service-account access token (ADC), potentially exposing Protected Health Information (PHI) and secondary Google Cloud Platform services.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16481.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-16481
- https://github.com/googleapis/mcp-toolbox/pull/3453
