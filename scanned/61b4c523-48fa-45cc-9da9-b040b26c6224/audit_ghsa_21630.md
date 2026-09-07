# [H] Cross site scripting in registration template in xwiki-platform

## Summary
Severity: High
Advisory: GHSA-gx6h-936c-vrrr
CVE: CVE-2022-23622
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-gx6h-936c-vrrr
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=2.6.1 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=13.0.0 <13.4.7
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=13.10.0 <13.10.3

## Details
### Impact

We found a possible XSS vector in the `registerinline.vm` template related to the `xredirect` hidden field. 
This template is only used in the following conditions:
  - the wiki must be open to registration for anyone
  - the wiki must be closed to view for Guest users (more specifically the XWiki.Registration page must be forbidden in View for guest user)

A way to obtain the second condition is when administrators checked the "Prevent unregistered users from viewing pages, regardless of the page rights" box in the administration rights.

### Patches

The issue is patched in versions 12.10.11, 14.0-rc-1, 13.4.7, 13.10.3.

### Workarounds

There are two main ways for protecting against this vulnerability, the easiest and the best one is by applying a patch in the `registerinline.vm` template, the patch consists in checking the value of the xredirect field to ensure it matches the following:
```
<input type="hidden" name="xredirect" value="$escapetool.xml($!request.xredirect)" />
```

If for some reason it's not possible to patch this file, another workaround is to ensure "Prevent unregistered users from viewing pages, regardless of the page rights" is not checked in the rights and apply a better right scheme using groups and rights on spaces. 

### References

https://jira.xwiki.org/browse/XWIKI-19291

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gx6h-936c-vrrr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23622
- https://github.com/xwiki/xwiki-platform/commit/053d957d53f2a543d158f3ab651e390d2728e0b9
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19291
