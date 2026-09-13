# [C] Craft CMS Allows Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-f3gw-9ww9-jmc3
CVE: CVE-2025-32432
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-04-25
Source: https://github.com/advisories/GHSA-f3gw-9ww9-jmc3
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=3.0.0-RC1 <3.9.15
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.14.15
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.6.17

## Details
### Impact

This is an additional fix for https://github.com/craftcms/cms/security/advisories/GHSA-4w8r-3xrw-v25g

This is a high-impact, low-complexity attack vector. To mitigate the issue, users running Craft installations before the fixed versions are encouraged to update to at least that version. 

### Details

https://craftcms.com/knowledge-base/craft-cms-cve-2025-32432

### References

https://github.com/craftcms/cms/commit/e1c85441fa47eeb7c688c2053f25419bc0547b47

https://github.com/craftcms/cms/blob/3.x/CHANGELOG.md#3915---2025-04-10-critical
https://github.com/craftcms/cms/blob/4.x/CHANGELOG.md#41415---2025-04-10-critical
https://github.com/craftcms/cms/blob/5.x/CHANGELOG.md#5617---2025-04-10-critical

https://sensepost.com/blog/2025/investigating-an-in-the-wild-campaign-using-rce-in-craftcms/

### Credits

Credit to [Orange Cyberdefense](https://github.com/Orange-Cyberdefense) for discovering a reporting this bug.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-4w8r-3xrw-v25g
- https://github.com/craftcms/cms/security/advisories/GHSA-f3gw-9ww9-jmc3
- https://nvd.nist.gov/vuln/detail/CVE-2025-32432
- https://github.com/craftcms/cms/commit/e1c85441fa47eeb7c688c2053f25419bc0547b47
- https://craftcms.com/knowledge-base/craft-cms-cve-2025-32432
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/3.x/CHANGELOG.md#3915---2025-04-10-critical
- https://github.com/craftcms/cms/blob/4.x/CHANGELOG.md#41415---2025-04-10-critical
- https://github.com/craftcms/cms/blob/5.x/CHANGELOG.md#5617---2025-04-10-critical
- https://sensepost.com/blog/2025/investigating-an-in-the-wild-campaign-using-rce-in-craftcms
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-32432
