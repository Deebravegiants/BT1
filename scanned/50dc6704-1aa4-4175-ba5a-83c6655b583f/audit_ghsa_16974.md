# [C] XWiki Platform CSRF remote code execution through the realtime HTML Converter API

## Summary
Severity: Critical
Advisory: GHSA-r5vh-gc3r-r24w
CVE: CVE-2024-31988
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-r5vh-gc3r-r24w
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-realtime-ui` — affected >=13.9-rc-1 <14.10.19
- Maven: `org.xwiki.platform:xwiki-platform-realtime-ui` — affected >=15.0-rc-1 <15.5.4
- Maven: `org.xwiki.platform:xwiki-platform-realtime-ui` — affected >=15.6-rc-1 <15.9

## Details
### Impact
When the realtime editor is installed in XWiki, it allows arbitrary remote code execution with the interaction of an admin user with programming right. More precisely, by getting an admin user to either visit a crafted URL or to view an image with this URL that could be in a comment, the attacker can get the admin to execute arbitrary XWiki syntax including scripting macros with Groovy or Python code. This compromises the confidentiality, integrity and availability of the whole XWiki installation.

To reproduce on an XWiki installation, as an admin, click on `<xwiki-host>/xwiki/bin/get/RTFrontend/ConvertHTML?wiki=xwiki&space=Main&page=WebHome&text=%7B%7Bvelocity%7D%7D%24logtool.error%28%22Hello%20from%20Velocity%20%21%22%29%7B%7B%2Fvelocity%7D%7D`. If the error "Hello from Velocity!" gets logged then the installation is vulnerable.

### Patches
This vulnerability has been patched in XWiki 14.10.19, 15.5.4 and 15.9.

### Workarounds
Update `RTFrontend.ConvertHTML` following this [patch](https://github.com/xwiki/xwiki-platform/commit/4896712ee6483da623f131be2e618f1f2b79cb8d#diff-32a2a63950724b24e63587570cd95a41cf689111b8ba61c48dabee9effec6d61).
This will, however, break some synchronization processes in the realtime editor, so upgrading should be the preferred way on installations where this editor is used.

### References
* https://jira.xwiki.org/browse/XWIKI-21424
* https://github.com/xwiki/xwiki-platform/commit/4896712ee6483da623f131be2e618f1f2b79cb8d

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-r5vh-gc3r-r24w
- https://nvd.nist.gov/vuln/detail/CVE-2024-31988
- https://github.com/xwiki/xwiki-platform/commit/4896712ee6483da623f131be2e618f1f2b79cb8d
- https://github.com/xwiki/xwiki-platform/commit/9f8cc88497418750b09ce9fde5d67d840f038fbf
- https://github.com/xwiki/xwiki-platform/commit/d88da4572fb7d4f95e1f54bb0cce33fce3df08d9
- https://github.com/xwiki/xwiki-platform/commit/d9f5043da289ff106f08e23576746fd8baf98794
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21424
