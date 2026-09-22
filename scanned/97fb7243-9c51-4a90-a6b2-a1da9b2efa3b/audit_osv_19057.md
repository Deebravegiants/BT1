# [H] CVE-2020-6581

## Summary
Severity: High
Advisory: CVE-2020-6581
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2020-6581
Type: osv

## Details
Nagios NRPE 3.2.1 has Insufficient Filtering because, for example, nasty_metachars interprets \n as the character \ and the character n (not as the \n newline sequence). This can cause command injection.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2DNGKXVDB43E3KQRA6W5QZT3Z46XZLQM/
- https://herolab.usd.de/security-advisories/
- https://herolab.usd.de/security-advisories/usd-2020-0002/
