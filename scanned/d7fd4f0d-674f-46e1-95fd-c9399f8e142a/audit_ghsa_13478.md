# [C] XWiki Platform vulnerable to XSS with edit right in the create document form for existing pages

## Summary
Severity: Critical
Advisory: GHSA-93gh-jgjj-r929
CVE: CVE-2023-45137
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-93gh-jgjj-r929
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=0 <14.10.12
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=15.0-rc-1 <15.5-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=3.1-milestone-2 <13.4-rc-1

## Details
### Impact
When trying to create a document that already exists, XWiki displays an error message in the form for creating it. Due to missing escaping, this error message is vulnerable to raw HTML injection and thus XSS. The injected code is the document reference of the existing document so this requires that the attacker first creates a non-empty document whose name contains the attack code. 

To reproduce, the following steps can be used:

1. Go to `<xwiki-host>/xwiki/bin/create/Main/WebHome?parent=&templateprovider=&spaceReference=&name=%3Cimg%20onerror=%22alert(1)%22%20src=%22test%22` where `<xwiki-host>` is the URL of your XWiki installation.
2. Create the page and add some content.
3. Go again to `<xwiki-host>/xwiki/bin/create/Main/WebHome?parent=&templateprovider=&spaceReference=&name=%3Cimg%20onerror=%22alert(1)%22%20src=%22test%22` where `<xwiki-host>` is the URL of your XWiki installation.

If an alert with content "1" is displayed, the installation is vulnerable. This allows an attacker to execute arbitrary actions with the rights of the user opening the malicious link. Depending on the rights of the user, this may allow remote code execution and full read and write access to the whole XWiki installation.

### Patches
This has been patched in XWiki 14.10.12 and 15.5RC1 by adding the appropriate escaping.

### Workarounds
The vulnerable template file createinline.vm is part of XWiki's WAR and can be patched by manually applying the [changes from the fix](https://github.com/xwiki/xwiki-platform/commit/ed8ec747967f8a16434806e727a57214a8843581#diff-c222148bddebe4ff7629350f4053b618504a4ab172e697938c8fddf7c1fc6bc8).

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-93gh-jgjj-r929
- https://nvd.nist.gov/vuln/detail/CVE-2023-45137
- https://github.com/xwiki/xwiki-platform/commit/ed8ec747967f8a16434806e727a57214a8843581
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20961
