# [M] CVE-2017-18018

## Summary
Severity: Medium
Advisory: CVE-2017-18018
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-04
Source: https://osv.dev/vulnerability/CVE-2017-18018
Type: osv

## Details
In GNU Coreutils through 8.29, chown-core.c in chown and chgrp does not prevent replacement of a plain file with a symlink during use of the POSIX "-R -L" options, which allows local users to modify the ownership of arbitrary files by leveraging a race condition.

## References
- http://lists.gnu.org/archive/html/coreutils/2017-12/msg00045.html
