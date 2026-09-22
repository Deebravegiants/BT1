# [C] XWiki Platform remote code execution from account via custom skins support

## Summary
Severity: Critical
Advisory: GHSA-cv55-v6rw-7r5v
CVE: CVE-2024-31987
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-cv55-v6rw-7r5v
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=6.4-milestone-1 <14.10.19
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0-rc-1 <15.5.4
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.6-rc-1 <15.10-rc-1

## Details
### Impact
Any user who can edit any page like their profile can create a custom skin with a template override that is executed with programming right, thus allowing remote code execution. 

To reproduce, as a user without edit, script or admin right, add an object of class `XWiki.XWikiSkins` to your profile. Name it whatever you want and set the Base Skin to `flamingo`.
Add an object of class `XWikiSkinFileOverrideClass` and set the path to `macros.vm` and the content to:
```
#macro(mediumUserAvatar $username)
  #resizedUserAvatar($username 50)
  $services.logging.getLogger('Skin').error("I got programming: $services.security.authorization.hasAccess('programming')")
#end
```
Back to your profile, click `Test this skin`. Force a refresh, just in case.
If the error "Skin - I got programming: true" gets logged, the installation is vulnerable.

### Patches
This has been patched in XWiki 14.10.19, 15.5.4 and 15.10RC1.

### Workarounds
We're not aware of any workaround except upgrading.

### References
* https://jira.xwiki.org/browse/XWIKI-21478
* https://github.com/xwiki/xwiki-platform/commit/3d4dbb41f52d1a6e39835cfb1695ca6668605a39 (>= 15.8 RC1)
* https://github.com/xwiki/xwiki-platform/commit/da177c3c972e797d92c1a31e278f946012c41b56 (< 15.8 RC1)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-cv55-v6rw-7r5v
- https://nvd.nist.gov/vuln/detail/CVE-2024-31987
- https://github.com/xwiki/xwiki-platform/commit/3d4dbb41f52d1a6e39835cfb1695ca6668605a39
- https://github.com/xwiki/xwiki-platform/commit/626d2a5dbf95b4e719ae13bf1a0a9c76e4edd5a2
- https://github.com/xwiki/xwiki-platform/commit/da177c3c972e797d92c1a31e278f946012c41b56
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21478
