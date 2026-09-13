# [M] Improper Authentication in infiniflow/ragflow

## Summary
Severity: Medium
Advisory: CVE-2024-12869
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12869
Type: osv

## Details
In infiniflow/ragflow version v0.12.0, there is an improper authentication vulnerability that allows a user to view another user's invite list. This can lead to a privacy breach where users' personal or private information, such as email addresses or usernames in the invite list, could be exposed without their consent. This data leakage can facilitate further attacks, such as phishing or spam, and result in loss of trust and potential regulatory issues.

## References
- https://huntr.com/bounties/768b1a56-1e79-416a-8445-65953568b04a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12869.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12869
