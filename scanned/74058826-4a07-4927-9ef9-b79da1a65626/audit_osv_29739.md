# [C] CVE-2024-45971

## Summary
Severity: Critical
Advisory: CVE-2024-45971
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-45971
Type: osv

## Details
Multiple Buffer overflows in the MMS Client in MZ Automation LibIEC61850 before commit 1f52be9ddeae00e69cd43e4cac3cb4f0c880c4f0 allow a malicious server to cause a stack-based buffer overflow via the MMS IdentifyResponse message.

## References
- https://encs.eu/news/critical-security-vulnerabilities-discovered-in-mz-automations-mms-client/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45971.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45971
- https://github.com/mz-automation/libiec61850/commit/1f52be9ddeae00e69cd43e4cac3cb4f0c880c4f0
