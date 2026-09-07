# [M] XWiki's scheduler in subwiki allows scheduling operations for any main wiki user

## Summary
Severity: Medium
Advisory: GHSA-cwq6-mjmx-47p6
CVE: CVE-2024-55876
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-cwq6-mjmx-47p6
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-scheduler-ui` — affected >=1.2-milestone-2 <15.10.9
- Maven: `org.xwiki.platform:xwiki-platform-scheduler-ui` — affected >=16.0.0-rc-1 <16.3.0

## Details
### Impact
Any user with an account on the main wiki could run scheduling operations on subwikis.
To reproduce, as a user on the main wiki without any special right, view the document `Scheduler.WebHome` in a subwiki. Then, click on any operation (*e.g.,* Trigger) on any job. If the operation is successful, then the instance is vulnerable.

### Patches
This has been patched in XWiki 15.10.9 and 16.3.0.

### Workarounds
If you have subwikis where the Job Scheduler is enabled, you can edit the objects on `Scheduler.WebPreferences` to match https://github.com/xwiki/xwiki-platform/commit/54bcc5a7a2e440cc591b91eece9c13dc0c487331#diff-8e274bd0065e319a34090339de6dfe56193144d15fd71c52c1be7272254728b4.

### References
* https://jira.xwiki.org/browse/XWIKI-21663
* https://github.com/xwiki/xwiki-platform/commit/54bcc5a7a2e440cc591b91eece9c13dc0c487331

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-cwq6-mjmx-47p6
- https://nvd.nist.gov/vuln/detail/CVE-2024-55876
- https://github.com/xwiki/xwiki-platform/commit/54bcc5a7a2e440cc591b91eece9c13dc0c487331
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21663
