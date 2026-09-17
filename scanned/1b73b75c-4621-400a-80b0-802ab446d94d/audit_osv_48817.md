# [H] CVE-2018-14624

## Summary
Severity: High
Advisory: CVE-2018-14624
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-14624
Type: osv

## Details
A vulnerability was discovered in 389-ds-base through versions 1.3.7.10, 1.3.8.8 and 1.4.0.16. The lock controlling the error log was not correctly used when re-opening the log file in log__error_emergency(). An attacker could send a flood of modifications to a very large DN, which would cause slapd to crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00033.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00037.html
- https://access.redhat.com/errata/RHSA-2018:2757
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14624
- https://pagure.io/389-ds-base/issue/49937
