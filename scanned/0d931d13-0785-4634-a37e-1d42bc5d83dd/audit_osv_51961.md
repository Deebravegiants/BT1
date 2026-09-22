# [M] CVE-2021-46671

## Summary
Severity: Medium
Advisory: CVE-2021-46671
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-02-04
Source: https://osv.dev/vulnerability/CVE-2021-46671
Type: osv

## Details
options.c in atftp before 0.7.5 reads past the end of an array, and consequently discloses server-side /etc/group data to a remote client.

## References
- https://lists.debian.org/debian-lts-announce/2022/05/msg00040.html
- https://bugs.debian.org/1004974
- https://sourceforge.net/p/atftp/code/ci/9cf799c40738722001552618518279e9f0ef62e5
