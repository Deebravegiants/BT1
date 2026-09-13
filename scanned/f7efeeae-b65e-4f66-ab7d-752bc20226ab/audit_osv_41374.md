# [M] Composio SDK < 0.2.32-beta.283 - Sensitive File Upload via tool-file-uploads.ts

## Summary
Severity: Medium
Advisory: CVE-2026-59807
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-59807
Type: osv

## Details
Composio SDK before 0.2.32-beta.283 contains a path validation bypass vulnerability that allows attackers to read and exfiltrate sensitive files by exploiting a missing assertSafeFileUploadPath check in the readFileFromDisk function within tool-file-uploads.ts. Attackers can exploit prompt injection to manipulate file_uploadable parameters to reference sensitive paths such as SSH private keys, causing the CLI to upload credential files to attacker-controlled storage.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59807.json
- https://github.com/ComposioHQ/composio/releases/tag/%40composio%2Fcli%400.2.32-beta.283
- https://nvd.nist.gov/vuln/detail/CVE-2026-59807
- https://www.vulncheck.com/advisories/composio-sdk-beta-283-sensitive-file-upload-via-tool-file-uploads-ts
- https://github.com/ComposioHQ/composio/pull/3763
- https://github.com/ComposioHQ/composio/commit/fc17c37bf95b7ece5c038cb7e2ab7e3e4a064e3a
- https://github.com/ComposioHQ/composio
- https://github.com/ComposioHQ/composio/issues/3746
