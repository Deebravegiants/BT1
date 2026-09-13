# [M] Velocity execution without script right through VelocityCode and VelocityWiki property

## Summary
Severity: Medium
Advisory: GHSA-m5m2-h6h9-p2c8
CVE: CVE-2023-41046
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-09-04
Source: https://github.com/advisories/GHSA-m5m2-h6h9-p2c8
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=7.2 <14.10.10
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0-rc-1 <15.4-rc-1

## Details
### Impact
It is possible in XWiki to execute Velocity code without having script right by creating an XClass with a property of type "TextArea" and content type "VelocityCode" or "VelocityWiki". For the former, the syntax of the document needs to be set the `xwiki/1.0` (this syntax doesn't need to be installed). In both cases, when adding the property to an object, the Velocity code is executed regardless of the rights of the author of the property (edit right is still required, though). In both cases, the code is executed with the correct context author so no privileged APIs can be accessed. However, Velocity still grants access to otherwise inaccessible data and APIs that could allow further privilege escalation.

At least for "VelocityCode", this behavior is most likely very old but only since XWiki 7.2, script right is a separate right, before that version all users were allowed to execute Velocity and thus this was expected and not a security issue.

### Patches
This has been patched in XWiki 14.10.10 and 15.4 RC1.

### Workarounds
There are no known workarounds.

### References
* https://jira.xwiki.org/browse/XWIKI-20847
* https://jira.xwiki.org/browse/XWIKI-20848
* https://github.com/xwiki/xwiki-platform/commit/edc52579eeaab1b4514785c134044671a1ecd839

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-m5m2-h6h9-p2c8
- https://nvd.nist.gov/vuln/detail/CVE-2023-41046
- https://github.com/xwiki/xwiki-platform/commit/edc52579eeaab1b4514785c134044671a1ecd839
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20847
- https://jira.xwiki.org/browse/XWIKI-20848
