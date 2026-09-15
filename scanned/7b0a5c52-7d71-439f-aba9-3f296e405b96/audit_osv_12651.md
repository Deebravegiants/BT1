# [M] CVE-2018-14017

## Summary
Severity: Medium
Advisory: CVE-2018-14017
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-12
Source: https://osv.dev/vulnerability/CVE-2018-14017
Type: osv

## Details
The r_bin_java_annotation_new function in shlr/java/class.c in radare2 2.7.0 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted .class file because of missing input validation in r_bin_java_line_number_table_attr_new.

## References
- https://github.com/radareorg/radare2/commit/e9ce0d64faf19fa4e9c260250fbdf25e3c11e152
- https://github.com/radare/radare2/issues/10498
