# [C] CVE-2020-14938

## Summary
Severity: Critical
Advisory: CVE-2020-14938
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-23
Source: https://osv.dev/vulnerability/CVE-2020-14938
Type: osv

## Details
An issue was discovered in map.c in FreedroidRPG 1.0rc2. It assumes lengths of data sets read from saved game files. It copies data from a file into a fixed-size heap-allocated buffer without size verification, leading to a heap-based buffer overflow.

## References
- https://bugs.freedroid.org/b/issue951
- https://logicaltrust.net/blog/2020/02/freedroid.html
