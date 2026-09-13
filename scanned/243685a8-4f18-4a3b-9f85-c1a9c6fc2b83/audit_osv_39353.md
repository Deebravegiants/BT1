# [M] Nextcloud: Calendar app leaked user identifiers via attendee suggestion endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-45286
Aliases: GHSA-r697-74m9-gvf2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45286
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From versions 5.5.13 to before 5.5.17, and 6.2.0 to before 6.2.3, an authenticated user can enumerate users on the same Nextcloud instance by using the Calendar app's endpoint for suggesting attendees. The sharing restrictions, applied to other endpoints, were not effective here. This issue has been patched in versions 5.5.17 and 6.2.3.

## References
- https://hackerone.com/reports/3540663
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45286.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-r697-74m9-gvf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45286
- https://github.com/nextcloud/calendar/issues/7971
- https://github.com/nextcloud/calendar/pull/8197
