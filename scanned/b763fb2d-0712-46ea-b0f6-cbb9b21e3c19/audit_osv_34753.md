# [H] MaxKB has SSRF in sandbox

## Summary
Severity: High
Advisory: CVE-2025-64511
Aliases: GHSA-9287-g7px-9rp4
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-64511
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. In versions prior to 2.3.1, a user can access internal network services such as databases through Python code in the tool module, although the process runs in a sandbox. Version 2.3.1 fixes the issue.

## References
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-9287-g7px-9rp4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64511.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64511
