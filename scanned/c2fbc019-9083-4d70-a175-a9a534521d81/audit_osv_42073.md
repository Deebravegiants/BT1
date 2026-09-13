# [H] staging: rtl8723bs: fix OOB reads in rtw_get_sec_ie(), rtw_get_wapi_ie(), and rtw_get_wps_attr()

## Summary
Severity: High
Advisory: CVE-2026-64441
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64441
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix OOB reads in rtw_get_sec_ie(), rtw_get_wapi_ie(), and rtw_get_wps_attr()

Three IE/attribute parsing functions have missing bounds checks.

rtw_get_sec_ie() and rtw_get_wapi_ie() iterate over a raw IE buffer
without verifying that the header bytes (tag + length) are within the
remaining buffer before reading them.  Additionally, rtw_get_sec_ie()
compares the 4-byte WPA OUI at cnt+2 without checking that at least
6 bytes remain, and rtw_get_wapi_ie() compares a 4-byte WAPI OUI at
cnt+6 without checking that at least 10 bytes remain.

rtw_get_wps_attr() reads wps_ie[0] and wps_ie+2 unconditionally at
entry, before verifying that wps_ielen is large enough to contain
the 6-byte WPS IE header (element_id + length + 4-byte OUI).  Inside
the attribute loop, get_unaligned_be16() is called on attr_ptr and
attr_ptr+2 without checking that 4 bytes remain in the buffer.

Add a cnt+2 bounds check before each loop body in rtw_get_sec_ie()
and rtw_get_wapi_ie(), guard each multi-byte comparison with a minimum
IE length requirement, add a wps_ielen < 6 early return in
rtw_get_wps_attr(), and add a 4-byte bounds check in its inner loop.

## References
- https://git.kernel.org/stable/c/1463ca3ec6601cbb097d8d87dbf5dcf1cb86a344
- https://git.kernel.org/stable/c/2ea1ce30ead61589214240e8d33d96310fd613e5
- https://git.kernel.org/stable/c/4b51ee8a40fe47864197d73cc02b191de7a6b072
- https://git.kernel.org/stable/c/6ab1161e539fb7a1c8b35ff5a6ced4702e855b9c
- https://git.kernel.org/stable/c/729c4e72563bda0f1725db1db9ea08df06f41d9b
- https://git.kernel.org/stable/c/b27ecba3196f6c14e3809595ebd69c0c2392512a
- https://git.kernel.org/stable/c/efa27d487abcdec79669a60a6d94d5d6eceb7c1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64441.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64441
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
