# [C] CVE-2019-19905

## Summary
Severity: Critical
Advisory: CVE-2019-19905
Aliases: GHSA-3cm7-rgh5-9pq5
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-19
Source: https://osv.dev/vulnerability/CVE-2019-19905
Type: osv

## Details
NetHack 3.6.x before 3.6.4 is prone to a buffer overflow vulnerability when reading very long lines from configuration files. This affects systems that have NetHack installed suid/sgid, and shared systems that allow users to upload their own configuration files.

## References
- https://github.com/NetHack/NetHack/security/advisories/GHSA-3cm7-rgh5-9pq5
- https://nethack.org/security/
- https://bugs.debian.org/947005
- https://github.com/NetHack/NetHack/commit/f001de79542b8c38b1f8e6d7eaefbbd28ab94b47
- https://github.com/NetHack/NetHack/commit/f4a840a48f4bcf11757b3d859e9d53cc9d5ef226
