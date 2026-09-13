# [H] CVE-2019-7347

## Summary
Severity: High
Advisory: CVE-2019-7347
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-7347
Type: osv

## Details
A Time-of-check Time-of-use (TOCTOU) Race Condition exists in ZoneMinder through 1.32.3 as a session remains active for an authenticated user even after deletion from the users table. This allows a nonexistent user to access and modify records (add/delete Monitors, Users, etc.).

## References
- https://github.com/ZoneMinder/zoneminder/issues/2476
