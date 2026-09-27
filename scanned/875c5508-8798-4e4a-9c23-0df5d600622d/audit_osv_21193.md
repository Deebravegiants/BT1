# [M] CVE-2021-41139

## Summary
Severity: Medium
Advisory: CVE-2021-41139
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-10-13
Source: https://osv.dev/vulnerability/CVE-2021-41139
Type: osv

## Details
Anuko Time Tracker is an open source, web-based time tracking application written in PHP. When a logged on user selects a date in Time Tracker, it is being passed on via the date parameter in URI. Because of not checking this parameter for sanity in versions prior to 1.19.30.5600, it was possible to craft the URI with malicious JavaScript, use social engineering to convince logged on user to click on such link, and have the attacker-supplied JavaScript to be executed in user's browser. This issue is patched in version 1.19.30.5600. As a workaround, one may introduce `ttValidDbDateFormatDate` function as in the latest version and add a call to it within the access checks block in time.php.

## References
- https://github.com/anuko/timetracker/security/advisories/GHSA-h2v8-87c9-86cw
- https://github.com/anuko/timetracker/commit/559906731f153c9b3a632c2839ed11669b76d593
- https://github.com/anuko/timetracker/commit/d3f60bd3e3ea8ff8ec31a596baec6750af601b7c
