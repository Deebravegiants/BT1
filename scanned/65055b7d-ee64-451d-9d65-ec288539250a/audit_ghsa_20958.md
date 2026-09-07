# [H] XWiki Platform Attachment UI vulnerable to cross-site scripting in the move attachment form

## Summary
Severity: High
Advisory: GHSA-9r9j-57rf-f6vj
CVE: CVE-2022-36097
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-9r9j-57rf-f6vj
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-attachment-ui` — affected >=14.0-rc-1 <14.4-rc-1

## Details
### Impact

It's possible to store JavaScript in an attachment name, which will be executed by anyone trying to move the corresponding attachment.

For example, an attachment with name `><img src=1 onerror=alert(1)>.jpg` will execute the alert.

### Patches
This issue has been patched in XWiki 14.4RC1.

### Workarounds
It is possible to fix the vulnerability by copying [moveStep1.vm](https://raw.githubusercontent.com/xwiki/xwiki-platform/xwiki-platform-14.0-rc-1/xwiki-platform-core/xwiki-platform-attachment/xwiki-platform-attachment-api/src/main/resources/templates/attachment/moveStep1.vm) to `webapp/xwiki/templates/moveStep1.vm` and replace 

```
#set($titleToDisplay = $services.localization.render('attachment.move.title', 
  [$attachment.name, $escapetool.xml($doc.plainTitle), $doc.getURL()]))
```

by 

```
#set($titleToDisplay = $services.localization.render('attachment.move.title', [
  $escapetool.xml($attachment.name), 
  $escapetool.xml($doc.plainTitle), 
  $escapetool.xml($doc.getURL())
]))
```

See the corresponding [patch](https://github.com/xwiki/xwiki-platform/commit/fbc4bfbae4f6ce8109addb281de86a03acdb9277).

### References

- https://jira.xwiki.org/browse/XWIKI-19667

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
- Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9r9j-57rf-f6vj
- https://nvd.nist.gov/vuln/detail/CVE-2022-36097
- https://github.com/xwiki/xwiki-platform/commit/fbc4bfbae4f6ce8109addb281de86a03acdb9277
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19667
- https://raw.githubusercontent.com/xwiki/xwiki-platform/xwiki-platform-14.0-rc-1/xwiki-platform-core/xwiki-platform-attachment/xwiki-platform-attachment-api/src/main/resources/templates/attachment/moveStep1.vm
