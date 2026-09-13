# [M] XWiki's REST APIs can list all pages/spaces, leading to unavailability

## Summary
Severity: Medium
Advisory: GHSA-mrqg-xmgm-rc5g
CVE: CVE-2026-40104
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-mrqg-xmgm-rc5g
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.8-rc-1 <16.10.16
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.0.0-rc-1 <17.4.8
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.5.0-rc-1 <17.10.1
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=1.8-rc-1 <16.10.16
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=17.0.0-rc-1 <17.4.8
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=17.5.0-rc-1 <17.10.1

## Details
### Impact
REST API endpoints like `/xwiki/rest/wikis/xwiki/spaces/AnnotationCode/pages/AnnotationConfig/objects/AnnotationCode.AnnotationConfig/0/properties` list all available pages as part of the metadata for database list properties, which can exhaust available resources on large wikis.

### Patches
This problem has been patched by applying the configured query limit also to the available values for database list properties in XWiki 16.10.16, 17.4.8 and 17.10.1.

### Workarounds
We're not aware of any workarounds apart from upgrading the affected modules.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-mrqg-xmgm-rc5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-40104
- https://github.com/xwiki/xwiki-platform/commit/47b568c4753a6e682b14be1ca581bdd3b25d45a7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23550
