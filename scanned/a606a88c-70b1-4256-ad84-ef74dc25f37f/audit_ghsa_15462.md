# [M] XWiki Platform document history including authors of any page exposed to unauthorized actors

## Summary
Severity: Medium
Advisory: GHSA-pvmm-55r5-g3mm
CVE: CVE-2024-45591
CWE: CWE-359, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-09-10
Source: https://github.com/advisories/GHSA-pvmm-55r5-g3mm
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=1.8.0 <15.10.9
- Maven: `org.xwiki.platform:xwiki-platform-rest-server` — affected >=16.0.0-rc-1 <16.3.0-rc-1

## Details
### Impact
The REST API exposes the history of any page in XWiki of which the attacker knows the name. The exposed information includes for each modification of the page the time of the modification, the version number, the author of the modification (both username and displayed name) and the version comment. This information is exposed regardless of the rights setup, and even when the wiki is configured to be fully private.

On a private wiki, this can be tested by accessing `/xwiki/rest/wikis/xwiki/spaces/Main/pages/WebHome/history`, if this shows the history of the main page then the installation is vulnerable.

### Patches
This has been patched in XWiki 15.10.9 and XWiki 16.3.0RC1.

### Workarounds
There aren't any known workarounds apart from upgrading to a fixed version.

### References
* https://jira.xwiki.org/browse/XWIKI-22052
* https://github.com/xwiki/xwiki-platform/commit/9cbca9808300797c67779bb9a665d85cf9e3d4b8

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-pvmm-55r5-g3mm
- https://nvd.nist.gov/vuln/detail/CVE-2024-45591
- https://github.com/xwiki/xwiki-platform/commit/26482ee5d29fc21f31134d1ee13db48716e89e0f
- https://github.com/xwiki/xwiki-platform/commit/9cbca9808300797c67779bb9a665d85cf9e3d4b8
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22052
