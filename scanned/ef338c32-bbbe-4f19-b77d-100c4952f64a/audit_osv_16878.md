# [C] CVE-2020-10232

## Summary
Severity: Critical
Advisory: CVE-2020-10232
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-09
Source: https://osv.dev/vulnerability/CVE-2020-10232
Type: osv

## Details
In version 4.8.0 and earlier of The Sleuth Kit (TSK), there is a stack buffer overflow vulnerability in the YAFFS file timestamp parsing logic in yaffsfs_istat() in fs/yaffs.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5EY53OYU7UZLAJWNIVVNR3EX2RNCCFTB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AQR2QY3IAF2IG6HGBSKGL66VUDOTC3OA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FFQKIE5U3LS5U7POPGS7YHLUSW2URWGJ/
- https://lists.debian.org/debian-lts-announce/2020/03/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/06/msg00015.html
- https://github.com/sleuthkit/sleuthkit/commit/459ae818fc8dae717549810150de4d191ce158f1
