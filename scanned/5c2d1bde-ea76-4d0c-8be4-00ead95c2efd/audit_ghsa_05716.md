# [M] XWiki Full Calendar Macro vulnerable to data leak through Calendar.JSONService

## Summary
Severity: Medium
Advisory: GHSA-637h-ch24-xp9m
CVE: CVE-2025-65090
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-637h-ch24-xp9m
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib:macro-fullcalendar-pom` — affected >=0 <2.4.6

## Details
### Impact
Anyone who has view rights on the `Calendar.JSONService` page, including guest users can exploit this vulnerability by accessing database info, with the exception of passwords.

### Workarounds
Remove the `Calendar.JSONService` page. This will however break some functionalities.

### References

Jira issue: 
* [FULLCAL-82: Calendar.JSONService exposes emails of all users](https://jira.xwiki.org/browse/FULLCAL-82)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki-contrib/macro-fullcalendar/security/advisories/GHSA-637h-ch24-xp9m
- https://nvd.nist.gov/vuln/detail/CVE-2025-65090
- https://github.com/xwiki-contrib/macro-fullcalendar/commit/25bc14c181c9a92f493b20ac264388c7ba171884
- https://github.com/xwiki-contrib/macro-fullcalendar
- https://jira.xwiki.org/browse/FULLCAL-82
