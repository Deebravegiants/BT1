# [H] Cross-Site Request Forgery (CSRF) allowing to delete or rename tags

## Summary
Severity: High
Advisory: GHSA-mq7h-5574-hw9f
CVE: CVE-2022-41927
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-mq7h-5574-hw9f
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-tag-ui` — affected >=3.2-milestone-2 <13.10.7
- Maven: `org.xwiki.platform:xwiki-platform-tag-ui` — affected >=14.0.0 <14.4.1

## Details
### Impact

It's possible with a simple request to perform deletion or renaming of tags without needing any confirmation, by using a CSRF attack. 

### Patches

The problem has been patched in XWiki 13.10.7, 14.4.1 and 14.5RC1. 

### Workarounds

It's possible to patch existing instances directly by editing the page Main.Tags and add this kind of check, in the code for renaming and for deleting:
```
#if (!$services.csrf.isTokenValid($request.get('form_token')))
    #set ($discard = $response.sendError(401, "Wrong CSRF token"))
#end
```

See the commit with the fix for more information about patching the page: https://github.com/xwiki/xwiki-platform/commit/7fd4cda0590180c4d34f557597e9e10e263def9e

### References

  * https://jira.xwiki.org/browse/XWIKI-19748
  * https://github.com/xwiki/xwiki-platform/commit/7fd4cda0590180c4d34f557597e9e10e263def9e

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-mq7h-5574-hw9f
- https://nvd.nist.gov/vuln/detail/CVE-2022-41927
- https://github.com/xwiki/xwiki-platform/commit/7fd4cda0590180c4d34f557597e9e10e263def9e
- https://github.com/xwiki/xwiki-platform
