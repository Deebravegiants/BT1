# [H] CVE-2018-6532

## Summary
Severity: High
Advisory: CVE-2018-6532
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2018-6532
Type: osv

## Details
An issue was discovered in Icinga 2.x through 2.8.1. By sending specially crafted (authenticated and unauthenticated) requests, an attacker can exhaust a lot of memory on the server side, triggering the OOM killer.

## References
- https://github.com/Icinga/icinga2/pull/6103
