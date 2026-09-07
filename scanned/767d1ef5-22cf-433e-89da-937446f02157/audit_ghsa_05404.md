# [M] TYPO3 CMS Allows Insecure Deserialization via Mailer File Spool

## Summary
Severity: Medium
Advisory: GHSA-7vp9-x248-9vr9
CVE: CVE-2026-0859
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:L/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-7vp9-x248-9vr9
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.0.2
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.23
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.41
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.49
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.55

## Details
### Problem
Local platform users who can write to TYPO3’s mail‑file spool directory can craft a file that the system will automatically deserialize without any class restrictions. This flaw allows an attacker to inject and execute arbitrary PHP code in the public scope of the web server.

The vulnerability is triggered when TYPO3 is configured with `$GLOBALS['TYPO3_CONF_VARS']['MAIL']['transport_spool_type'] = 'file';` and a scheduler task or cron job runs the command `mailer:spool:send`. The spool‑send operation performs the insecure deserialization that is at the core of this issue.

### Solution
Update to TYPO3 versions 10.4.55 ELTS, 11.5.49 ELTS, 12.4.41 LTS, 13.4.23 LTS, 14.0.2 that fix the problem described.

### Credits
Thanks to Vitaly Simonovich for reporting this issue, and to TYPO3 security team members Elias Häußler and Oliver Hader for fixing it.

### References
* [TYPO3-CORE-SA-2026-004](https://typo3.org/security/advisory/typo3-core-sa-2026-004)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-7vp9-x248-9vr9
- https://nvd.nist.gov/vuln/detail/CVE-2026-0859
- https://github.com/TYPO3/typo3/commit/3225d705080a1bde57a66689621c947da5a4782f
- https://github.com/TYPO3/typo3/commit/722bf71c118b0a8e4f2c2494854437d846799a13
- https://github.com/TYPO3/typo3/commit/e0f0ceee480c203fbb60b87454f5f193e541d27f
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-004
