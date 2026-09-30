# [H] CVE-2020-11033

## Summary
Severity: High
Advisory: CVE-2020-11033
Aliases: GHSA-rf54-3r4w-4h55
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-05
Source: https://osv.dev/vulnerability/CVE-2020-11033
Type: osv

## Details
In GLPI from version 9.1 and before version 9.4.6, any API user with READ right on User itemtype will have access to full list of users when querying apirest.php/User. The response contains: - All api_tokens which can be used to do privileges escalations or read/update/delete data normally non accessible to the current user. - All personal_tokens can display another users planning. Exploiting this vulnerability requires the api to be enabled, a technician account. It can be mitigated by adding an application token. This is fixed in version 9.4.6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5WQMONZRWLWOXMHMYWR7A5Q5JJERPMVC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q4BG2UTINBVV7MTJRXKBQ26GV2UINA6L/
- https://github.com/glpi-project/glpi/security/advisories/GHSA-rf54-3r4w-4h55
