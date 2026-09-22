# [M] Nextcloud Desktop client misbehaves with E2EE when the server returns empty list of metadata keys

## Summary
Severity: Medium
Advisory: CVE-2023-28998
Aliases: GHSA-jh3g-wpwv-cqgr
CVSS: 6.7 (CVSS:3.1/AV:P/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2023-28998
Type: osv

## Details
The Nextcloud Desktop Client is a tool to synchronize files from Nextcloud Server. Starting with version 3.0.0 and prior to version 3.6.5, a malicious server administrator can gain full access to an end-to-end encrypted folder. They can decrypt files, recover the folder structure, and add new files.​ Users should upgrade the Nextcloud Desktop client to 3.6.5 to receive a patch. No known workarounds are available.

## References
- https://ethz.ch/content/dam/ethz/special-interest/infk/inst-infsec/appliedcrypto/education/theses/report_DanieleCoppola.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28998.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-jh3g-wpwv-cqgr
- https://nvd.nist.gov/vuln/detail/CVE-2023-28998
- https://github.com/nextcloud/desktop/pull/5323
