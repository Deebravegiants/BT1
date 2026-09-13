# [M] CVE-2017-13756

## Summary
Severity: Medium
Advisory: CVE-2017-13756
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13756
Type: osv

## Details
In The Sleuth Kit (TSK) 4.4.2, opening a crafted disk image triggers infinite recursion in dos_load_ext_table() in tsk/vs/dos.c in libtskvs.a, as demonstrated by mmls.

## References
- https://lists.debian.org/debian-lts-announce/2022/06/msg00015.html
- https://github.com/sleuthkit/sleuthkit/issues/914
