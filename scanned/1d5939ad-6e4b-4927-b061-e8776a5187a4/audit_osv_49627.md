# [H] CVE-2019-14866

## Summary
Severity: High
Advisory: CVE-2019-14866
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-07
Source: https://osv.dev/vulnerability/CVE-2019-14866
Type: osv

## Details
In all versions of cpio before 2.13 does not properly validate input files when generating TAR archives. When cpio is used to create TAR archives from paths an attacker can write to, the resulting archive may contain files with permissions the attacker did not have or in paths he did not have access to. Extracting those archives from a high-privilege user without carefully reviewing them may lead to the compromise of the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00007.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14866
- https://lists.gnu.org/archive/html/bug-cpio/2019-08/msg00003.html
- https://lists.gnu.org/archive/html/bug-cpio/2019-11/msg00000.html
