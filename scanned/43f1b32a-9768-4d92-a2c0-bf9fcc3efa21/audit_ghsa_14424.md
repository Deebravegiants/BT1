# [C] XWiki Platform users may execute anything with superadmin right through comments and async macro

## Summary
Severity: Critical
Advisory: GHSA-9cqm-5wf7-wcj7
CVE: CVE-2023-26471
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-9cqm-5wf7-wcj7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rendering-async-macro` — affected >=11.6-rc-1 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-rendering-async-macro` — affected >=14.0 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-rendering-async-macro` — affected >=14.5 <14.9

## Details
### Impact

Comments are supposed to be executed with the right of superadmin but in restricted mode (anything dangerous is disabled) but the async macro is not taking into account the restricted mode.

This means that any user with comment right can use the async macro to make it execute any wiki content with the right of superadmin as in:

{{async}}
{{groovy}}println "it works !"{{/groovy}}
{{/async}}

### Patches

This has been patched in XWiki 14.9, 14.4.6, and 13.10.10.

### Workarounds

The only known workaround consists in applying [the following patch](https://github.com/xwiki/xwiki-platform/commit/00532d9f1404287cf3ec3a05056640d809516006) and rebuilding and redeploying `org.xwiki.platform:xwiki-platform-rendering-async-macro`.

### References

* https://jira.xwiki.org/browse/XWIKI-20234

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](http://jira.xwiki.org)
* Email us at [Security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9cqm-5wf7-wcj7
- https://nvd.nist.gov/vuln/detail/CVE-2023-26471
- https://github.com/xwiki/xwiki-platform/commit/00532d9f1404287cf3ec3a05056640d809516006
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20234
