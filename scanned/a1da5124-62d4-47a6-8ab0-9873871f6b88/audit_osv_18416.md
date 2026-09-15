# [C] CVE-2020-27602

## Summary
Severity: Critical
Advisory: CVE-2020-27602
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2020-27602
Type: osv

## Details
BigBlueButton before 2.2.7 does not have a protection mechanism for separator injection in meetingId, userId, and authToken.

## References
- https://github.com/bigbluebutton/bigbluebutton/compare/v2.2.6...v2.2.7
- https://github.com/bigbluebutton/bigbluebutton/commit/4bfd924c64da2681f4c037026021f47eb189d717
