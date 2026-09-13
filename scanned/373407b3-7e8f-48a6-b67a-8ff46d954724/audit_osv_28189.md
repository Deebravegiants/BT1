# [M] JumpServer allows nn authorized attacker to get sensitive information in playbook files when playbook_id is leaked

## Summary
Severity: Medium
Advisory: CVE-2024-29020
Aliases: GHSA-7mqc-23hr-cr62
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-03-29
Source: https://osv.dev/vulnerability/CVE-2024-29020
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. An authorized attacker can obtain sensitive information contained within playbook files if they manage to learn the playbook_id of another user. This breach of confidentiality can lead to information disclosure and exposing sensitive data. This vulnerability is fixed in v3.10.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29020.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-7mqc-23hr-cr62
- https://nvd.nist.gov/vuln/detail/CVE-2024-29020
