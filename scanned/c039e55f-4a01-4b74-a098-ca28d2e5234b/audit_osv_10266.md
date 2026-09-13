# [H] CVE-2017-14639

## Summary
Severity: High
Advisory: CVE-2017-14639
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14639
Type: osv

## Details
AP4_VisualSampleEntry::ReadFields in Core/Ap4SampleEntry.cpp in Bento4 1.5.0-617 uses incorrect character data types, which causes a stack-based buffer underflow and out-of-bounds write, leading to denial of service (application crash) or possibly unspecified other impact.

## References
- https://blogs.gentoo.org/ago/2017/09/14/bento4-stack-based-buffer-underflow-in-ap4_visualsampleentryreadfields-ap4sampleentry-cpp/
- https://github.com/axiomatic-systems/Bento4/commit/03d1222ab9c2ce779cdf01bdb96cdd69cbdcfeda
- https://github.com/axiomatic-systems/Bento4/issues/190
