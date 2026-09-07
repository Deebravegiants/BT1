# [C] XWiki Full Calendar Macro vulnerable to SQL injection through Calendar.JSONService

## Summary
Severity: Critical
Advisory: GHSA-2g22-wg49-fgv5
CVE: CVE-2025-65091
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-2g22-wg49-fgv5
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib:macro-fullcalendar-pom` — affected >=0 <2.4.5

## Details
### Impact

Anyone who has view rights on the `Calendar.JSONService` page, including guest users can exploit this vulnerability by accessing database info or starting a DoS attack.

### Workarounds

Remove the `Calendar.JSONService` page. This will however break some functionalities.

### References

Jira issue: 
* [FULLCAL-80: SQL injection through Calendar.JSONService](https://jira.xwiki.org/browse/FULLCAL-80)
* [FULLCAL-81: SQL injection through Calendar.JSONService still exists](https://jira.xwiki.org/browse/FULLCAL-81)

### For more information

If there are any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki-contrib/macro-fullcalendar/security/advisories/GHSA-2g22-wg49-fgv5
- https://nvd.nist.gov/vuln/detail/CVE-2025-65091
- https://github.com/xwiki-contrib/macro-fullcalendar/commit/5fdcf06a05015786492fda69b4d9dea5460cc994
- https://github.com/xwiki-contrib/macro-fullcalendar
