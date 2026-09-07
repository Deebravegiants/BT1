# [C] XWiki Change Request Application UI XSS and remote code execution through change request title

## Summary
Severity: Critical
Advisory: GHSA-f776-w9v2-7vfj
CVE: CVE-2023-45138
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-f776-w9v2-7vfj
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.changerequest:application-changerequest-ui` — affected >=0.11 <1.9.2

## Details
### Impact

It's possible for a user without any specific right to perform script injection and remote code execution just by inserting an appropriate title when creating a new Change Request. 
This vulnerability is particularly critical as Change Request aims at being created by user without any particular rights.

### Patches

The vulnerability has been fixed in Change Request 1.9.2. 

### Workarounds

It's possible to workaround the issue without upgrading by editing the document `ChangeRequest.Code.ChangeRequestSheet` and by performing the same change as in the commit: https://github.com/xwiki-contrib/application-changerequest/commit/7565e720117f73102f5a276239eabfe85e15cff4. 

### References

  * JIRA ticket: https://jira.xwiki.org/browse/CRAPP-298
  * Commit of the fix: https://github.com/xwiki-contrib/application-changerequest/commit/7565e720117f73102f5a276239eabfe85e15cff4

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

Thanks Michael Hamann for the report.

## References
- https://github.com/xwiki-contrib/application-changerequest/security/advisories/GHSA-f776-w9v2-7vfj
- https://nvd.nist.gov/vuln/detail/CVE-2023-45138
- https://github.com/xwiki-contrib/application-changerequest/commit/7565e720117f73102f5a276239eabfe85e15cff4
- https://github.com/xwiki-contrib/application-changerequest
- https://jira.xwiki.org/browse/CRAPP-298
