# [C] XWiki Platform vulnerable to code injection from account through XWiki.SchedulerJobSheet

## Summary
Severity: Critical
Advisory: GHSA-fc42-5w56-qw7h
CVE: CVE-2023-29524
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-fc42-5w56-qw7h
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-scheduler-ui` — affected >=2.0.1 <14.10.3

## Details
### Impact

It's possible to execute anything with the right of the Scheduler Application sheet page.

To reproduce:
1. As a user without script or programming rights, edit your user profile with the object editor and add a new object of type XWiki.SchedulerJobClass (search for "Scheduler")
1. In "Job Script", add the following
  ```{{/code}} {{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("Hello " + "from groovy!"){{/groovy} {{/async}}```
1. Click "Save & View"
1. If the job information isn't already displayed (you should see "Job Name", "Job Description", etc.), append ?sheet=XWiki.SchedulerJobSheet to the URL.

### Patches

This has been patched in XWiki 14.10.3 and 15.0 RC1.

### Workarounds

While the fix in the scheduler itself is easy, it relies on the code macro `source` parameter, which was introduced in 14.10.2 so you have to upgrade to benefit from it.

### References

https://jira.xwiki.org/browse/XWIKI-20295
https://jira.xwiki.org/browse/XWIKI-20462

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-fc42-5w56-qw7h
- https://nvd.nist.gov/vuln/detail/CVE-2023-29524
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20295
- https://jira.xwiki.org/browse/XWIKI-20462
