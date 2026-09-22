# [M] Nextcloud Desktop: Initialization vector reuse in E2EE allows malicious server admin to break, manipulate, access files

## Summary
Severity: Medium
Advisory: CVE-2023-28997
Aliases: GHSA-4p33-rw27-j5fc
CVSS: 6.7 (CVSS:3.1/AV:P/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2023-04-04
Source: https://osv.dev/vulnerability/CVE-2023-28997
Type: osv

## Details
The Nextcloud Desktop Client is a tool to synchronize files from Nextcloud Server. Starting with version 3.0.0 and prior to version 3.6.5, a malicious server administrator can recover and modify the contents of end-to-end encrypted files. Users should upgrade the Nextcloud Desktop client to 3.6.5 to receive a patch. No known workarounds are available.

## References
- https://ethz.ch/content/dam/ethz/special-interest/infk/inst-infsec/appliedcrypto/education/theses/report_DanieleCoppola.pdf
- https://lists.debian.org/debian-lts-announce/2025/09/msg00018.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28997.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-4p33-rw27-j5fc
- https://nvd.nist.gov/vuln/detail/CVE-2023-28997
- https://github.com/nextcloud/desktop/pull/5324
