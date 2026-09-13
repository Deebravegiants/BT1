# [M] CVE-2017-13755

## Summary
Severity: Medium
Advisory: CVE-2017-13755
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13755
Type: osv

## Details
In The Sleuth Kit (TSK) 4.4.2, opening a crafted ISO 9660 image triggers an out-of-bounds read in iso9660_proc_dir() in tsk/fs/iso9660_dent.c in libtskfs.a, as demonstrated by fls.

## References
- https://lists.debian.org/debian-lts-announce/2022/06/msg00015.html
- https://github.com/sleuthkit/sleuthkit/issues/913
