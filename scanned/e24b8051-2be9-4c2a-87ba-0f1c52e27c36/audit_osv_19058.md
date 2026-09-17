# [H] CVE-2020-6582

## Summary
Severity: High
Advisory: CVE-2020-6582
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2020-6582
Type: osv

## Details
Nagios NRPE 3.2.1 has a Heap-Based Buffer Overflow, as demonstrated by interpretation of a small negative number as a large positive number during a bzero call.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2DNGKXVDB43E3KQRA6W5QZT3Z46XZLQM/
- https://herolab.usd.de/security-advisories/
- https://herolab.usd.de/security-advisories/usd-2020-0001/
