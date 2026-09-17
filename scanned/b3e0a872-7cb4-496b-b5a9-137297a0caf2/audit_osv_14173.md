# [C] CVE-2018-7648

## Summary
Severity: Critical
Advisory: CVE-2018-7648
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/CVE-2018-7648
Type: osv

## Details
An issue was discovered in mj2/opj_mj2_extract.c in OpenJPEG 2.3.0. The output prefix was not checked for length, which could overflow a buffer, when providing a prefix with 50 or more characters on the command line.

## References
- https://github.com/uclouvain/openjpeg/issues/1088
- https://github.com/uclouvain/openjpeg/commit/cc3824767bde397fedb8a1ae4786a222ba860c8d
