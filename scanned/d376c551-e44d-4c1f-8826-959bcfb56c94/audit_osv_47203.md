# [M] CVE-2016-10374

## Summary
Severity: Medium
Advisory: CVE-2016-10374
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-05-17
Source: https://osv.dev/vulnerability/CVE-2016-10374
Type: osv

## Details
perltidy through 20160302, as used by perlcritic, check-all-the-things, and other software, relies on the current working directory for certain output files and does not have a symlink-attack protection mechanism, which allows local users to overwrite arbitrary files by creating a symlink, as demonstrated by creating a perltidy.ERR symlink that the victim cannot delete.

## References
- https://bugs.debian.org/862667
