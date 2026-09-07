# [H] N8N's Chat Trigger component is vulnerable to XSS

## Summary
Severity: High
Advisory: GHSA-v2x8-97xq-8xrr
CVE: CVE-2025-56265
CWE: CWE-434, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-v2x8-97xq-8xrr
Type: github-advisory

## Affected
- npm: `@n8n/n8n-nodes-langchain` — affected >=0 <1.107.0

## Details
An arbitrary file upload vulnerability in the Chat Trigger component of N8N v1.95.3, v1.100.1, and v1.101.1 allows attackers to execute arbitrary code via uploading a crafted HTML file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56265
- https://github.com/n8n-io/n8n/pull/18148
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%401.107.0
- https://github.com/nikolas-ch/CVEs/blob/main/N8N/N8N_v1.100.1/ChatTrigger_StoredXSSviaUnrestrictedFileUpload/StoredXSSviaUnristrictedFileUpload.txt
