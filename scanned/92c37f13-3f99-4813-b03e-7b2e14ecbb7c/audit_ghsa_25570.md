# [M] Incorrect Use of Privileged APIs in org.xwiki.platform.skin.skinx

## Summary
Severity: Medium
Advisory: GHSA-ghcq-472w-vf4h
CVE: CVE-2022-24821
CWE: CWE-648
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-ghcq-472w-vf4h
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-skin-skinx` — affected >=13.5.0 <13.10
- Maven: `org.xwiki.platform:xwiki-platform-skin-skinx` — affected >=0 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-skin-skinx` — affected >=13.0.0 <13.4.6

## Details
### Impact

Simple users can create global SSX/JSX without specific rights: in theory only users with Programming Rights should be allowed to create SSX or JSX that are executed everywhere on a wiki. But a bug allow anyone with edit rights to actually create those. 

### Patches
This issue has been patched in XWiki 13.10-rc-1, 12.10.11 and 13.4.6. 

### Workarounds
There's no easy workaround for this issue, administrators should upgrade their wiki.

### References
https://jira.xwiki.org/browse/XWIKI-19155

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [XWiki Security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-ghcq-472w-vf4h
- https://nvd.nist.gov/vuln/detail/CVE-2022-24821
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19155
