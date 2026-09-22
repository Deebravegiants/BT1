# [C] CVE-2017-9433

## Summary
Severity: Critical
Advisory: CVE-2017-9433
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9433
Type: osv

## Details
Document Liberation Project libmwaw before 2017-04-08 has an out-of-bounds write caused by a heap-based buffer overflow related to the MsWrd1Parser::readFootnoteCorrespondance function in lib/MsWrd1Parser.cxx.

## References
- http://www.debian.org/security/2017/dsa-3875
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1037
- https://sourceforge.net/p/libmwaw/libmwaw/ci/68b3b74569881248bfb6cbb4266177cc253b292f/
