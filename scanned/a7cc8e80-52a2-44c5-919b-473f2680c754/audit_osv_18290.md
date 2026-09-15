# [M] CVE-2020-25820

## Summary
Severity: Medium
Advisory: CVE-2020-25820
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-21
Source: https://osv.dev/vulnerability/CVE-2020-25820
Type: osv

## Details
BigBlueButton before 2.2.7 allows remote authenticated users to read local files and conduct SSRF attacks via an uploaded Office document that has a crafted URL in an ODF xlink field.

## References
- https://github.com/bigbluebutton/bigbluebutton/compare/v2.2.26...v2.2.27
- https://www.redteam-pentesting.de/advisories/rt-sa-2020-005
- https://github.com/bigbluebutton/bigbluebutton/commit/71fe1eac1e5bd73a2cd44bd79c001086b250e435
- http://packetstormsecurity.com/files/159667/BigBlueButton-2.2.25-File-Disclosure-Server-Side-Request-Forgery.html
- https://www.golem.de/news/big-blue-button-das-grosse-blaue-sicherheitsrisiko-2010-151610.html
