# [M] CVE-2025-51459

## Summary
Severity: Medium
Advisory: CVE-2025-51459
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-51459
Type: osv

## Details
File Upload vulnerability in agent.hub.controller.refresh_plugins in eosphoros-ai DB-GPT 0.7.0 allows remote attackers to execute arbitrary code via a malicious plugin ZIP file uploaded to the /v1/personal/agent/upload endpoint, interacting with plugin_hub._sanitize_filename and plugins_util.scan_plugins.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51459.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51459
- https://github.com/eosphoros-ai/DB-GPT/pull/2649
- https://www.gecko.security/blog/cve-2025-51459
