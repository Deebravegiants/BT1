# [C] CVE-2025-8454

## Summary
Severity: Critical
Advisory: CVE-2025-8454
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2025-8454
Type: osv

## Details
It was discovered that uscan, a tool to scan/watch upstream sources for new releases of software, included in devscripts (a collection of scripts to make the life of a Debian Package maintainer easier), skips OpenPGP verification if the upstream source is already downloaded from a previous run even if the verification failed back then.

## References
- https://bugs.debian.org/1109251
