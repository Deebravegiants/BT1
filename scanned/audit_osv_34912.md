# [H] MaxKB vulnerable to privilege escalation through sandbox bypass

## Summary
Severity: High
Advisory: CVE-2025-66419
Aliases: GHSA-f9qm-2pxq-fx6c
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-66419
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. In versions 2.3.1 and below, the tool module allows an attacker to escape the sandbox environment and escalate privileges under certain concurrent conditions. This issue is fixed in version 2.4.0.

## References
- https://github.com/1Panel-dev/MaxKB/releases/tag/v2.4.0
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-f9qm-2pxq-fx6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66419.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66419
- https://github.com/1Panel-dev/MaxKB/commit/f8ada9a110c4dbef8c3c2636c78847ecd621ece7
