# [M] direct_mail for Typo3 sensitive data exposure

## Summary
Severity: Medium
Advisory: GHSA-j2w4-45qm-r674
CVE: CVE-2019-16698
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j2w4-45qm-r674
Type: github-advisory

## Affected
- Packagist: `directmailteam/direct-mail` — affected >=0 <5.2.3

## Details
The direct_mail (aka Direct Mail) extension through 5.2.2 for TYPO3 has a missing access check in the backend module, allowing a user (with restricted permissions to the fe_users table) to view and export data of frontend users who are subscribed to a newsletter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16698
- https://github.com/kartolo/direct_mail/commit/3a70924777294c7fb40e9f6eb3f7627bac58dfd1
- https://extensions.typo3.org/extension/direct_mail
- https://github.com/kartolo/direct_mail
- https://typo3.org/security/advisory/typo3-ext-sa-2019-016
