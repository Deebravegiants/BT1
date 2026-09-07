# [C] plone.app.event vulnerable to denial of service via iCalendar import

## Summary
Severity: Critical
Advisory: GHSA-r82h-mqw3-fc56
CVE: CVE-2026-55247
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-r82h-mqw3-fc56
Type: github-advisory

## Affected
- PyPI: `plone.app.event` — affected >=0 <5.2.4
- PyPI: `plone.app.event` — affected >=6.0.0a1 <6.0.1

## Details
### Impact
By abusing the iCalendar import functionality, a logged-in editor could take the whole site offline, make the server reach into the internal network and read calendar files off disk (SSRF), and store XSS.

### Patches
The problem has been patched in `plone.app.event`.

* For Plone 6.2: upgrade to `plone.app.event` 6.0.1
* For Plone 6.1: upgrade to `plone.app.event` 5.2.4
* For Plone 6.0: upgrade to `plone.app.event` 5.2.4

### Workarounds
In the site root, go to the Security tab of the Zope Management Interface (`manage_access`), look for the "plone.app.event: Import Ical" permission, and grant this only to the Manager role.  Then only users with the Manager role can use the ical import form.

There is no workaround for the stored XSS in the URL field of events.

The vulnerabilities were discovered by Timothy Dudley and responsibly reported to the [Plone Security Team](mailto:security@plone.org). Thank you!

## References
- https://github.com/plone/plone.app.event/security/advisories/GHSA-r82h-mqw3-fc56
- https://github.com/plone/plone.app.event/commit/1e3c83c15a24d1a789cdb012593505bc5620e28e
- https://github.com/plone/plone.app.event/commit/4de5eb3ea9e4f7f1781622e6d64fc086629d1437
- https://github.com/plone/plone.app.event
- https://github.com/plone/plone.app.event/releases/tag/5.2.4
- https://github.com/plone/plone.app.event/releases/tag/6.0.1
