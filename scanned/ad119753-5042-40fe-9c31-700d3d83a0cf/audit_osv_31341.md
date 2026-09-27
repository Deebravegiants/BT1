# [H] Remote Code Execution in transformeroptimus/superagi

## Summary
Severity: High
Advisory: CVE-2024-9439
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9439
Type: osv

## Details
SuperAGI is vulnerable to remote code execution in the latest version. The `agent template update` API allows attackers to control certain parameters, which are then fed to the eval function without any sanitization or checks in place. This vulnerability can lead to full system compromise.

## References
- https://huntr.com/bounties/d710884f-b5ab-4b31-a2e6-e4b38488def1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9439.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9439
