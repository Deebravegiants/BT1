# [C] XWiki Platform web templates vulnerable to reflected XSS in the create document form if name validation is enabled

## Summary
Severity: Critical
Advisory: GHSA-qcj9-gcpg-4w2w
CVE: CVE-2023-45136
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-qcj9-gcpg-4w2w
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=12.0-rc-1 <14.10.12
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=15.0-rc-1 <15.5-rc-1

## Details
### Impact
When document names are validated according to a name strategy (disabled by default), XWiki is vulnerable to a reflected XSS attack in the page creation form. To reproduce, make sure that "Validate names before saving" is enabled in the administration under "Editing" -> "Name strategies" and then open `<xwiki-host>/xwiki/bin/create/Main/%3Cscript%3Ealert%28%27Test%20Test%20Test%20Test%20Test%27%29%3C%2Fscript%3E` where `<xwiki-host>` is the URL of your XWiki installation. This displays an alert if the installation is vulnerable. This allows an attacker to execute arbitrary actions with the rights of the user opening the malicious link. Depending on the rights of the user, this may allow remote code execution and full read and write access to the whole XWiki installation.

### Patches
This has been patched in XWiki 14.10.12 and 15.5-RC-1 by adding appropriate escaping.

### Workarounds
The vulnerable template file `createinline.vm` is part of XWiki's WAR and can be patched by manually applying the [changes from the fix](https://github.com/xwiki/xwiki-platform/commit/ba56fda175156dd35035f2b8c86cbd8ef1f90c2e#diff-c222148bddebe4ff7629350f4053b618504a4ab172e697938c8fddf7c1fc6bc8).

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qcj9-gcpg-4w2w
- https://nvd.nist.gov/vuln/detail/CVE-2023-45136
- https://github.com/xwiki/xwiki-platform/commit/ba56fda175156dd35035f2b8c86cbd8ef1f90c2e
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20854
