# [M] CVE-2018-19497

## Summary
Severity: Medium
Advisory: CVE-2018-19497
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-29
Source: https://osv.dev/vulnerability/CVE-2018-19497
Type: osv

## Details
In The Sleuth Kit (TSK) through 4.6.4, hfs_cat_traverse in tsk/fs/hfs.c does not properly determine when a key length is too large, which allows attackers to cause a denial of service (SEGV on unknown address with READ memory access in a tsk_getu16 call in hfs_dir_open_meta_cb in tsk/fs/hfs_dent.c).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LZXFYOOMSP7NWRTSO4XXGHXAY3CJNAJ6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NLSVLDQLPGKRHHBPYUXVJJPAID6CYBXD/
- https://lists.debian.org/debian-lts-announce/2018/12/msg00008.html
- https://lists.debian.org/debian-lts-announce/2022/06/msg00015.html
- https://github.com/sleuthkit/sleuthkit/commit/bc04aa017c0bd297de8a3b7fc40ffc6ddddbb95d
- https://github.com/sleuthkit/sleuthkit/pull/1374
