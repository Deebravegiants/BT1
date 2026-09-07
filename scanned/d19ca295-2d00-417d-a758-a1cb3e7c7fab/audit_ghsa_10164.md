# [H] TYPO3 CMS Stores Cleartext Password in User Settings Module

## Summary
Severity: High
Advisory: GHSA-xvv6-p4wf-mvx7
CVE: CVE-2026-6553
CWE: CWE-312
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-xvv6-p4wf-mvx7
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=14.2.0 <14.3.0

## Details
### Problem
The backend user settings module (`SetupModuleController`) incorrectly conflates entity data (like passwords or email address) with user-interface settings (like theme, display options) when persisting changes. As a result, passwords were stored in cleartext in the `uc` and `user_settings` fields of the `be_users` database table.

The cleartext data was only persisted if users changed their credentials in the backend user settings module when the TYPO3 14.2.0 release was used (not in any other version).

### Solution
Update to TYPO3 version 14.3.0 LTS which fixes the problem described.

> [!IMPORTANT]
> **Manual actions required**
> 
> Updating to the patched release does not retroactively clean existing data. It is recommended to execute all User Settings upgrade wizards in the TYPO3 Install Tool, including the dedicated User Settings Scrubbing wizard, which sanitizes the incorrectly persisted cleartext values from the `uc` and `user_settings` fields of the `be_users` table. **Additionally, affected backend user accounts should be assigned new passwords.**
> 
> _Admin Tools → Upgrade → Upgrade Wizard → User Settings Scrubbing_

### Credits
TYPO3 thanks Martin Clewing for reporting this issue, and TYPO3 core team members Oliver Hader, Stefan Bürk and Garvin Hicking for fixing it.

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-xvv6-p4wf-mvx7
- https://nvd.nist.gov/vuln/detail/CVE-2026-6553
- https://github.com/TYPO3/typo3/commit/9a6e913f70767f63b322ae3e2d2f4e302624c291
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-005
