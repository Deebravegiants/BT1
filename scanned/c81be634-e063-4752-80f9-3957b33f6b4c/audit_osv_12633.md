# [C] CVE-2018-13846

## Summary
Severity: Critical
Advisory: CVE-2018-13846
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-13846
Type: osv

## Details
An issue has been found in Bento4 1.5.1-624. AP4_Mpeg2TsVideoSampleStream::WriteSample in Core/Ap4Mpeg2Ts.cpp has a heap-based buffer over-read after a call from Mp42Ts.cpp, a related issue to CVE-2018-14532.

## References
- https://github.com/axiomatic-systems/Bento4/issues/282
