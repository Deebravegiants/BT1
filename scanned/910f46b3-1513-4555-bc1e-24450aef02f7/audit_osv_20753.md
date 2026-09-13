# [H] CVE-2021-36691

## Summary
Severity: High
Advisory: CVE-2021-36691
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2021-36691
Type: osv

## Details
libjxl v0.5.0 is affected by a Assertion failed issue in lib/jxl/image.cc jxl::PlaneBase::PlaneBase(). When encoding a malicous GIF file using cjxl, an attacker can trigger a denial of service.

## References
- https://github.com/libjxl/libjxl/issues/422
