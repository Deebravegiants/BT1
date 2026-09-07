# [H] Cross-site Scripting in the Flamingo theme manager

## Summary
Severity: High
Advisory: GHSA-vmhh-xh3g-j992
CVE: CVE-2022-29251
CWE: CWE-116, CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-vmhh-xh3g-j992
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-theme-ui` — affected >=0 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-theme-ui` — affected >=13.0.0 <13.4.7
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-theme-ui` — affected >=13.5.0 <13.10.3

## Details
### Impact
We found a possible XSS vector in the `FlamingoThemesCode.WebHomeSheet` wiki page related to the "newThemeName" form field.

### Patches

The issue is patched in versions 12.10.11, 14.0-rc-1, 13.4.7, 13.10.3.

### Workarounds
The easiest workaround is to edit the wiki page `FlamingoThemesCode.WebHomeSheet` (with wiki editor) and change the line

```
<input type="hidden" name="newThemeName" id="newThemeName" value="$request.newThemeName" />
```

into

```
<input type="hidden" name="newThemeName" id="newThemeName" value="$escapetool.xml($request.newThemeName)" />
```

### References
  * https://jira.xwiki.org/browse/XWIKI-19294
  * https://github.com/xwiki/xwiki-platform/commit/bd935320bee3c27cf7548351b1d0f935f116d437

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-vmhh-xh3g-j992
- https://nvd.nist.gov/vuln/detail/CVE-2022-29251
- https://github.com/xwiki/xwiki-platform/commit/bd935320bee3c27cf7548351b1d0f935f116d437
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19294
