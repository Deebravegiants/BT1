# [C] Exposure of Private Personal Information to an Unauthorized Actor in alextselegidis/easyappointments

## Summary
Severity: Critical
Advisory: GHSA-r6cm-wg48-rh2r
CVE: CVE-2022-0482
CWE: CWE-359, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-10
Source: https://github.com/advisories/GHSA-r6cm-wg48-rh2r
Type: github-advisory

## Affected
- Packagist: `alextselegidis/easyappointments` — affected >=0 <1.4.3

## Details
The software is a booking management system that has a public form to place bookings, and a private area for the calendar and management of services, users, settings, etc. There is a backend API that allows data manipulation, including listing the appointments for a specific time range. This happens on this endpoint: /index.php/backend_api/ajax_get_calendar_events Unfortunately, there is no authentication / permissions-check on that endpoint, the only required parameters in a POST request are "startDate", "endDate" and "csrfToken". Because the csrfToken can be obtained by any unauthenticated user just visiting the public form (and is valid for the backend as well), any attacker can query the backend API and obtain all sorts of private information about the appointment, in JSON format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0482
- https://github.com/alextselegidis/easyappointments/commit/44af526a6fc5e898bc1e0132b2af9eb3a9b2c466
- https://github.com/alextselegidis/easyappointments
- https://github.com/alextselegidis/easyappointments/releases/tag/1.4.3
- https://huntr.dev/bounties/2fe771ef-b615-45ef-9b4d-625978042e26
- https://opencirt.com/hacking/securing-easy-appointments-cve-2022-0482
- http://packetstormsecurity.com/files/166701/Easy-Appointments-Information-Disclosure.html
