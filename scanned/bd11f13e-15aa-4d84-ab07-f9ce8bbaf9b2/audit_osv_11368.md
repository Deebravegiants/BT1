# [C] CVE-2017-7555

## Summary
Severity: Critical
Advisory: CVE-2017-7555
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-17
Source: https://osv.dev/vulnerability/CVE-2017-7555
Type: osv

## Details
Augeas versions up to and including 1.8.0 are vulnerable to heap-based buffer overflow due to improper handling of escaped strings. Attacker could send crafted strings that would cause the application using augeas to copy past the end of a buffer, leading to a crash or possible code execution.

## References
- https://puppet.com/security/cve/cve-2017-7555
- http://www.debian.org/security/2017/dsa-3949
- http://www.securityfocus.com/bid/100378
- https://access.redhat.com/errata/RHSA-2017:2788
- https://access.redhat.com/errata/RHSA-2019:2403
- https://github.com/hercules-team/augeas/pull/480
