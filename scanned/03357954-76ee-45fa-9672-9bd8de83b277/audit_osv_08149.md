# [C] CVE-2016-10722

## Summary
Severity: Critical
Advisory: CVE-2016-10722
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/CVE-2016-10722
Type: osv

## Details
partclone.fat in Partclone before 0.2.88 is prone to a heap-based buffer overflow vulnerability due to insufficient validation of the FAT superblock, related to the mark_reserved_sectors function. An attacker may be able to execute arbitrary code in the context of the user running the affected application.

## References
- https://github.com/Thomas-Tsai/partclone/issues/71
- https://david.gnedt.at/blog/2016/11/14/advisory-partclone-fat-bitmap-heap-overflow/
