# [M] n8n before 1.123.73 Local File Read and SSRF via Gmail and Brevo nodes

## Summary
Severity: Medium
Advisory: CVE-2026-85170
Aliases: GHSA-95ph-833c-4wrp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85170
Type: osv

## Details
n8n versions before 1.123.73, 2.35.4, and 2.36.2 pass message content in the Gmail (v1) and Brevo nodes to the mail composer without verifying it is a string. An authenticated user able to run a workflow can supply an expression that resolves to an object carrying a path or href property, causing the composer to read a local file accessible to the n8n process or fetch an internal URL (SSRF) and attach the result to the outgoing message.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85170.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-95ph-833c-4wrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-85170
- https://www.vulncheck.com/advisories/n8n-before-1.123.73-local-file-read-and-ssrf-via-gmail-and-brevo-nodes
