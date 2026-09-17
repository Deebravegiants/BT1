# [C] CVE-2021-21352

## Summary
Severity: Critical
Advisory: CVE-2021-21352
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-03-03
Source: https://osv.dev/vulnerability/CVE-2021-21352
Type: osv

## Details
Anuko Time Tracker is an open source, web-based time tracking application written in PHP. In TimeTracker before version 1.19.24.5415 tokens used in password reset feature in Time Tracker are based on system time and, therefore, are predictable. This opens a window for brute force attacks to guess user tokens and, once successful, change user passwords, including that of a system administrator. This vulnerability is pathced in version 1.19.24.5415 (started to use more secure tokens) with an additional improvement in 1.19.24.5416 (limited an available window for brute force token guessing).

## References
- https://www.anuko.com/time-tracker/index.htm
- https://github.com/anuko/timetracker/security/advisories/GHSA-43c9-rx4h-4gqq
- https://github.com/anuko/timetracker/commit/40f3d9345adc20e6f28eb9f59e2489aff87fecf5
