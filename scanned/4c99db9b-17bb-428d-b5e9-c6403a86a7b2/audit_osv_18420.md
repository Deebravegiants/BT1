# [M] CVE-2020-27606

## Summary
Severity: Medium
Advisory: CVE-2020-27606
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-10-21
Source: https://osv.dev/vulnerability/CVE-2020-27606
Type: osv

## Details
BigBlueButton before 2.2.28 (or earlier) does not set the secure flag for the session cookie in an https session, which makes it easier for remote attackers to capture this cookie by intercepting its transmission within an http session.

## References
- https://www.golem.de/news/big-blue-button-das-grosse-blaue-sicherheitsrisiko-2010-151610.html
