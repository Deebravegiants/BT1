# [M] Nextcloud Desktop client behaves incorrectly if the initial end-to-end-encryption signature is empty

## Summary
Severity: Medium
Advisory: CVE-2024-52510
Aliases: GHSA-r4qc-m9mj-452v
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52510
Type: osv

## Details
The Nextcloud Desktop Client is a tool to synchronize files from Nextcloud Server with your computer. The Desktop client did not stop with an error but allowed by-passing the signature validation, if a manipulated server sends an empty initial signature. It is recommended that the Nextcloud Desktop client is upgraded to 3.14.2 or later.

## References
- https://hackerone.com/reports/2597504
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52510.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-r4qc-m9mj-452v
- https://nvd.nist.gov/vuln/detail/CVE-2024-52510
- https://github.com/nextcloud/desktop/commit/97539218e6f63c3a3fd1694cb7d8aef27c5910d7
- https://github.com/nextcloud/desktop/pull/7333
