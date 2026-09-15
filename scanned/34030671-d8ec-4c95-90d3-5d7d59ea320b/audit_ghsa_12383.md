# [H] Data leak of password hash through change requests

## Summary
Severity: High
Advisory: GHSA-2fr7-cc7p-p45q
CVE: CVE-2023-49280
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-2fr7-cc7p-p45q
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.changerequest:application-changerequest-default` — affected >=0.1 <1.10

## Details
### Impact

Change request allows to edit any page by default, and the changes are then exported in an XML that anyone can download. So it's possible for an attacker to obtain password hash of users by performing edition of the user profiles and then downloading the XML that has been created. This is also true for any document that might contain password field and that a user can view.
This vulnerability impacts all version of Change Request, but the impact depends on the rights that has been set on the wiki since it requires for the user to have the Change request right (allowed by default) and view rights on the page to target. 
Also the issue cannot be easily exploited in an automated way. 

### Patches

The patch consists in denying to users the right of editing pages that contains a password field with change request. It means that already existing change request for those pages won't be removed by the patch, administrators needs to take care of it. 

The patch is provided in Change Request 1.10, administrators should upgrade immediately. 

### Workarounds

It's possible to workaround the vulnerability by denying manually the Change request right on some spaces, such as XWiki space which will include any user profile by default. 

### References

  * JIRA issue: https://jira.xwiki.org/browse/CRAPP-302
  * Commit of the fix: https://github.com/xwiki-contrib/application-changerequest/commit/ff0f5368ea04f0e4aa7b33821c707dc68a8c5ca8

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

Thanks Michael Hamann for the report.

## References
- https://github.com/xwiki-contrib/application-changerequest/security/advisories/GHSA-2fr7-cc7p-p45q
- https://nvd.nist.gov/vuln/detail/CVE-2023-49280
- https://github.com/xwiki-contrib/application-changerequest/commit/ff0f5368ea04f0e4aa7b33821c707dc68a8c5ca8
- https://github.com/xwiki-contrib/application-changerequest
- https://jira.xwiki.org/browse/CRAPP-302
