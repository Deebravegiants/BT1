# [H] CVE-2020-35702

## Summary
Severity: High
Advisory: CVE-2020-35702
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-25
Source: https://osv.dev/vulnerability/CVE-2020-35702
Type: osv

## Details
DCTStream::getChars in DCTStream.cc in Poppler 20.12.1 has a heap-based buffer overflow via a crafted PDF document. NOTE: later reports indicate that this only affects builds from Poppler git clones in late December 2020, not the 20.12.1 release. In this situation, it should NOT be considered a Poppler vulnerability. However, several third-party Open Source projects directly rely on Poppler git clones made at arbitrary times, and therefore the CVE remains useful to users of those projects

## References
- https://gitlab.freedesktop.org/poppler/poppler/-/issues/1011
