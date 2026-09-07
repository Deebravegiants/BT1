# [M] XWiki Platform Stored Cross-site Scripting in the user profile via the timezone displayer

## Summary
Severity: Medium
Advisory: GHSA-h8cm-3v5f-rgp6
CVE: CVE-2023-40176
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-h8cm-3v5f-rgp6
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=4.1-milestone-2 <14.10.5

## Details
### Impact

Any registered user can exploit a stored XSS through their user profile by setting the payload as the value of the time zone user preference. Even though the time zone is selected from a drop down (no free text value) it can still be set from JavaScript (using the browser developer tools) or by calling the save URL on the user profile with the right query string. Once the time zone is set it is displayed without escaping which means the payload gets executed for any user that visits the malicious user profile, allowing the attacker to steal information and even gain more access rights (escalation to programming rights).

The problem is present [since version 4.1M2](https://jira.xwiki.org/browse/XWIKI-7847) when the time zone user preference was introduced.

### Patches

The issue has been fixed in XWiki 14.10.5 and 15.1RC1 by https://github.com/xwiki/xwiki-platform/commit/d11ca5d781f8a42a85bc98eb82306c1431e764d4 . The main fix is in the [``displayer_timezone.vm``](https://github.com/xwiki/xwiki-platform/commit/d11ca5d781f8a42a85bc98eb82306c1431e764d4#diff-57ffb6e10fa8768e59948f2becf755699570d97b78bb12a9623e0de49e6c5c7d) precisely at this [line](https://github.com/xwiki/xwiki-platform/commit/d11ca5d781f8a42a85bc98eb82306c1431e764d4#diff-57ffb6e10fa8768e59948f2becf755699570d97b78bb12a9623e0de49e6c5c7dR40):

    $!escapetool.xml($value)

By escaping the displayed time zone value we make sure the attacker's payload is not executed.

### Workarounds

If you want to fix this problem on older versions of XWiki that have not been patched then you need to edit ``displayer_timezone.vm`` and escape the displayed time zone value [here](https://github.com/xwiki/xwiki-platform/blob/xwiki-platform-14.10.4/xwiki-platform-core/xwiki-platform-web/xwiki-platform-web-templates/src/main/resources/templates/displayer_timezone.vm#L32):

```
- $!value
+ $!escapetool.xml($value)
```

### References

* JIRA issue https://jira.xwiki.org/browse/XWIKI-20276
* Fix https://github.com/xwiki/xwiki-platform/commit/d11ca5d781f8a42a85bc98eb82306c1431e764d4

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been found and reported by @michitux .

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h8cm-3v5f-rgp6
- https://nvd.nist.gov/vuln/detail/CVE-2023-40176
- https://github.com/xwiki/xwiki-platform/commit/d11ca5d781f8a42a85bc98eb82306c1431e764d4
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-7847
