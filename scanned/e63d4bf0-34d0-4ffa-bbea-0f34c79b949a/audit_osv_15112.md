# [C] CVE-2019-1353

## Summary
Severity: Critical
Advisory: CVE-2019-1353
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/CVE-2019-1353
Type: osv

## Details
An issue was found in Git before v2.24.1, v2.23.1, v2.22.2, v2.21.1, v2.20.2, v2.19.3, v2.18.2, v2.17.3, v2.16.6, v2.15.4, and v2.14.6. When running Git in the Windows Subsystem for Linux (also known as "WSL") while accessing a working directory on a regular Windows drive, none of the NTFS protections were active.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00003.html
- https://lore.kernel.org/git/xmqqr21cqcn9.fsf%40gitster-ct.c.googlers.com/T/#u
- https://public-inbox.org/git/xmqqr21cqcn9.fsf%40gitster-ct.c.googlers.com/
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00056.html
- https://security.gentoo.org/glsa/202003-30
