# [M] XWiki vulnerable to click-jacking through CSS injection in comments

## Summary
Severity: Medium
Advisory: GHSA-74rh-c5rh-88vg
CVE: CVE-2026-26000
CWE: CWE-1021
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-74rh-c5rh-88vg
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=17.5.0 <17.9.0
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=17.0.0-rc-1 <17.4.6
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=0 <16.10.13

## Details
### Impact

It's possible using comments to inject CSS that would transform the full wiki in a link area leading to a malicious page. All versions of XWiki are impacted by this kind of attack. 

### Patches

The problem has been patched not by preventing injecting CSS in comments, which is currently a feature of XWiki, but by requiring confirmation from users when driving them to untrusted domains after clicking on a link, thus preventing any click-jacking attack. 
This security measure has been put in place in XWiki 17.9.0, 17.4.6, 16.10.13.

### Workarounds

There's no out-of-the-box workaround, but it should be possible to partly reuse [the javascript code provided for the security measure](https://github.com/xwiki/xwiki-platform/blob/xwiki-platform-17.9.0/xwiki-platform-core/xwiki-platform-web/xwiki-platform-web-war/src/main/webapp/resources/uicomponents/link/link-protection.js) in a JSX object inside the wiki, to request the same kind of confirmation. 

### References
  * JIRA ticket: https://jira.xwiki.org/browse/XWIKI-23433
  * Documentation of the new security measure: https://www.xwiki.org/xwiki/bin/view/ReleaseNotes/Data/XWiki/17.9.0RC1/Entry006/
  * Commit for the security fix: https://github.com/xwiki/xwiki-platform/commit/29cb81f3a5387cf822d7e7534bdd63903275f86b

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

Thanks Tomas Keech (Sentrium Security Ltd) for reporting this vulnerability.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-74rh-c5rh-88vg
- https://nvd.nist.gov/vuln/detail/CVE-2026-26000
- https://github.com/xwiki/xwiki-platform/pull/4645
- https://github.com/xwiki/xwiki-platform/commit/29cb81f3a5387cf822d7e7534bdd63903275f86b
- https://github.com/xwiki/xwiki-platform/commit/7b5a4f8c34d9b1da3d966e17f7dbccabac448e75
- https://github.com/xwiki/xwiki-platform
- https://github.com/xwiki/xwiki-platform/releases/tag/xwiki-platform-17.4.6
- https://jira.xwiki.org/browse/XWIKI-23433
- https://www.xwiki.org/xwiki/bin/view/ReleaseNotes/Data/XWiki/17.9.0RC1/Entry006
