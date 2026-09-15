# [C] CVE-2017-9432

## Summary
Severity: Critical
Advisory: CVE-2017-9432
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9432
Type: osv

## Details
Document Liberation Project libstaroffice before 2017-04-07 has an out-of-bounds write caused by a stack-based buffer overflow related to the DatabaseName::read function in lib/StarWriterStruct.cxx.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1029
- https://github.com/fosnola/libstaroffice/commit/2d6253c7a692a3d92785dd990fce7256ea05e794
