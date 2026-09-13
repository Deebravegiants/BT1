# [M] Craft CMS Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-j5g9-j7r4-6qvx
CVE: CVE-2024-21622
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-j5g9-j7r4-6qvx
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.5.11
- Packagist: `craftcms/cms` — affected >=3.0.0 <3.9.6

## Details
### Impact

This is a potential moderate impact, low complexity privilege escalation vulnerability in Craft with certain user permissions setups.

### Patches

This has been fixed in Craft 4.4.16 and Craft 3.9.6. Users should ensure they are running at least those versions.

### References

https://github.com/craftcms/cms/pull/13932
https://github.com/craftcms/cms/pull/13931
https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#4511---2023-11-16
https://github.com/craftcms/cms/blob/v3/CHANGELOG.md#396---2023-11-16

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-j5g9-j7r4-6qvx
- https://nvd.nist.gov/vuln/detail/CVE-2024-21622
- https://github.com/craftcms/cms/pull/13931
- https://github.com/craftcms/cms/pull/13932
- https://github.com/craftcms/cms/commit/76caf9af07d9964be0fd362772223be6a5f5b6aa
- https://github.com/craftcms/cms/commit/be81eb653d633833f2ab22510794abb6bb9c0843
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#4511---2023-11-16
- https://github.com/craftcms/cms/blob/v3/CHANGELOG.md#396---2023-11-16
