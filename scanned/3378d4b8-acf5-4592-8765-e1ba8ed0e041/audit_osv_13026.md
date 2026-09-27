# [H] CVE-2018-16889

## Summary
Severity: High
Advisory: CVE-2018-16889
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-28
Source: https://osv.dev/vulnerability/CVE-2018-16889
Type: osv

## Details
Ceph does not properly sanitize encryption keys in debug logging for v4 auth. This results in the leaking of encryption key information in log files via plaintext. Versions up to v13.2.4 are vulnerable.

## References
- https://usn.ubuntu.com/4035-1/
- http://www.securityfocus.com/bid/106528
- https://access.redhat.com/errata/RHSA-2019:2538
- https://access.redhat.com/errata/RHSA-2019:2541
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16889
