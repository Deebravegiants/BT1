# [C] CVE-2017-15994

## Summary
Severity: Critical
Advisory: CVE-2017-15994
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-29
Source: https://osv.dev/vulnerability/CVE-2017-15994
Type: osv

## Details
rsync 3.1.3-development before 2017-10-24 mishandles archaic checksums, which makes it easier for remote attackers to bypass intended access restrictions. NOTE: the rsync development branch has significant use beyond the rsync developers, e.g., the code has been copied for use in various GitHub projects.

## References
- https://git.samba.org/?p=rsync.git%3Ba=commit%3Bh=7b8a4ecd6ff9cdf4e5d3850ebf822f1e989255b3
- https://git.samba.org/?p=rsync.git%3Ba=commit%3Bh=9a480deec4d20277d8e20bc55515ef0640ca1e55
- https://git.samba.org/?p=rsync.git%3Ba=commit%3Bh=c252546ceeb0925eb8a4061315e3ff0a8c55b48b
