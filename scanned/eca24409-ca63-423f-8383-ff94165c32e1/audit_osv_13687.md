# [H] CVE-2018-20819

## Summary
Severity: High
Advisory: CVE-2018-20819
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-23
Source: https://osv.dev/vulnerability/CVE-2018-20819
Type: osv

## Details
io/ZlibCompression.cc in the decompression component in Dropbox Lepton 1.2.1 allows attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact by crafting a jpg image file. The root cause is a missing check of header payloads that may be (incorrectly) larger than the maximum file size.

## References
- https://github.com/dropbox/lepton/issues/112
