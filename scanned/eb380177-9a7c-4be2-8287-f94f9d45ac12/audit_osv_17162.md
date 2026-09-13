# [M] CVE-2020-13230

## Summary
Severity: Medium
Advisory: CVE-2020-13230
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-05-20
Source: https://osv.dev/vulnerability/CVE-2020-13230
Type: osv

## Details
In Cacti before 1.2.11, disabling a user account does not immediately invalidate any permissions granted to that account (e.g., permission to view logs).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ICJMWSY77IIGZYR6FE6NAQZFBO42VECO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q3PCDGNELH7HEBIXRNT5J5EWQEXQAU6B/
- https://github.com/Cacti/cacti/releases/tag/release%2F1.2.11
- https://lists.debian.org/debian-lts-announce/2022/03/msg00038.html
- https://github.com/Cacti/cacti/issues/3343
