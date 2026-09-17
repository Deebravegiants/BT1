# [M] CVE-2020-28954

## Summary
Severity: Medium
Advisory: CVE-2020-28954
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-11-19
Source: https://osv.dev/vulnerability/CVE-2020-28954
Type: osv

## Details
web/controllers/ApiController.groovy in BigBlueButton before 2.2.29 lacks certain parameter sanitization, as demonstrated by accepting control characters in a user name.

## References
- https://github.com/bigbluebutton/bigbluebutton/compare/v2.2.28...v2.2.29
- https://github.com/bigbluebutton/bigbluebutton/issues/10818
- https://github.com/bigbluebutton/bigbluebutton/commit/5c911ddeec4493f40f42e2f137800ed4692004a4
- https://github.com/bigbluebutton/bigbluebutton/commit/e59bcd0c33a6a3203c011faa8823ba2cac1e4f37
