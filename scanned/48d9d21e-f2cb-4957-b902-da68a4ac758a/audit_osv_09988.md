# [H] CVE-2017-12596

## Summary
Severity: High
Advisory: CVE-2017-12596
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-07
Source: https://osv.dev/vulnerability/CVE-2017-12596
Type: osv

## Details
In OpenEXR 2.2.0, a crafted image causes a heap-based buffer over-read in the hufDecode function in IlmImf/ImfHuf.cpp during exrmaketiled execution; it may result in denial of service or possibly unspecified other impact.

## References
- https://github.com/openexr/openexr/releases/tag/v2.3.0
- https://lists.debian.org/debian-lts-announce/2020/08/msg00056.html
- https://usn.ubuntu.com/4148-1/
- https://github.com/openexr/openexr/issues/238
- https://github.com/xiaoqx/pocs/blob/master/openexr.md
