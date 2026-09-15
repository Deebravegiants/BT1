# [C] XWiki Platform: Remote code execution from edit in multilingual wikis via translations

## Summary
Severity: Critical
Advisory: GHSA-xxp2-9c9g-7wmj
CVE: CVE-2024-31983
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-xxp2-9c9g-7wmj
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-localization-source-wiki` — affected >=4.3-milestone-2 <14.10.20
- Maven: `org.xwiki.platform:xwiki-platform-localization-source-wiki` — affected >=15.0-rc-1 <15.5.4
- Maven: `org.xwiki.platform:xwiki-platform-localization-source-wiki` — affected >=15.6-rc-1 <15.10-rc-1

## Details
### Impact

In multilingual wikis, translations can be edited by any user who has edit right, circumventing the rights that are normally required for authoring translations (script right for user-scope translations, wiki admin for translations on the wiki). This can be exploited for remote code execution if the translation value is not properly escaped where it is used. To reproduce, in a multilingual wiki, as a user without script or admin right, edit a translation of `AppWithinMinutes.Translations` and in the line `platform.appwithinminutes.description=`  add `{{async}}{{groovy}}println("Hello from Translation"){{/groovy}}{{/async}}` at the end. Then open the app with in minutes home page (`AppWithinMinutes.WebHome`) in the same locale. If translations are still working and "Hello from Translation" is displayed at the end of the introduction, the installation is vulnerable.

### Patches
This has been patched in XWiki 14.10.20, 15.5.4 and 15.10RC1.

### Workarounds
We're not aware of any workaround except restricting edit right on documents that contain translations.

### References
* https://jira.xwiki.org/browse/XWIKI-21411
* https://github.com/xwiki/xwiki-platform/commit/c4c8d61c30de72298d805ccc82df2a307f131c54

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-xxp2-9c9g-7wmj
- https://nvd.nist.gov/vuln/detail/CVE-2024-31983
- https://github.com/xwiki/xwiki-platform/commit/2a9ce88f33663c53c9c63b2ea573f4720ea2efb9
- https://github.com/xwiki/xwiki-platform/commit/73aef9648bbff04b697837f1b906932f0d5caacb
- https://github.com/xwiki/xwiki-platform/commit/c4c8d61c30de72298d805ccc82df2a307f131c54
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21411
