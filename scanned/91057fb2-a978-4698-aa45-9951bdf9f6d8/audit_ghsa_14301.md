# [H] XWiki Platform vulnerable to code injection from account/view through VFS Tree macro

## Summary
Severity: High
Advisory: GHSA-p67q-h88v-5jgr
CVE: CVE-2023-29521
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-p67q-h88v-5jgr
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-vfs-ui` — affected >=7.4-milestone-2 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-vfs-ui` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-vfs-ui` — affected >=14.5 <14.10.2

## Details
### Impact
Any user with view rights can execute arbitrary Groovy, Python or Velocity code in XWiki leading to full access to the XWiki installation. The root cause is improper escaping of `Macro.VFSTreeMacro`. This page is not installed by default.

See https://jira.xwiki.org/browse/XWIKI-20260 for the reproduction steps.

### Patches
The vulnerability has been patched in XWiki 15.0-rc-1, 14.10.2, 14.4.8, 13.10.11.

### Workarounds
The issue can be fixed by applying this [patch](https://github.com/xwiki/xwiki-platform/commit/fad02328f5ec7ab7fe5b932ffb5bc5c1ba7a5b12) on `Macro.VFSTreeMacro`.

### References
- https://jira.xwiki.org/browse/XWIKI-20260
- https://github.com/xwiki/xwiki-platform/commit/fad02328f5ec7ab7fe5b932ffb5bc5c1ba7a5b12

### For more information

If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p67q-h88v-5jgr
- https://nvd.nist.gov/vuln/detail/CVE-2023-29521
- https://github.com/xwiki/xwiki-platform/commit/fad02328f5ec7ab7fe5b932ffb5bc5c1ba7a5b12
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20260
