# [M] CVE-2017-11353

## Summary
Severity: Medium
Advisory: CVE-2017-11353
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11353
Type: osv

## Details
yadm (yet another dotfile manager) 1.10.0 has a race condition (related to the behavior of git commands in setting permissions for new files and directories), which potentially allows access to SSH and PGP keys.

## References
- https://bugs.debian.org/868300
- https://github.com/TheLocehiliosan/yadm/issues/74
