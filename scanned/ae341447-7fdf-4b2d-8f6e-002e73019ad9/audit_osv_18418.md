# [M] CVE-2020-27604

## Summary
Severity: Medium
Advisory: CVE-2020-27604
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-21
Source: https://osv.dev/vulnerability/CVE-2020-27604
Type: osv

## Details
BigBlueButton before 2.3 does not implement LibreOffice sandboxing. This might make it easier for remote authenticated users to read the API shared secret in the bigbluebutton.properties file. With the API shared secret, an attacker can (for example) use api/join to join an arbitrary meeting regardless of its guestPolicy setting.

## References
- https://docs.bigbluebutton.org/dev/api.html
- https://www.golem.de/news/big-blue-button-das-grosse-blaue-sicherheitsrisiko-2010-151610.html
