# [H] staging: rtl8723bs: fix OOB reads in is_ap_in_tkip() IE loop

## Summary
Severity: High
Advisory: CVE-2026-64536
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64536
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix OOB reads in is_ap_in_tkip() IE loop

The loop in is_ap_in_tkip() iterates over IEs without verifying that
enough bytes remain before dereferencing the IE header or its payload:

- pIE->element_id and pIE->length are read without checking that
  i + sizeof(*pIE) <= ie_length, so a truncated IE at the end of the
  buffer causes an OOB read.

- For WLAN_EID_VENDOR_SPECIFIC the code compares pIE->data + 12,
  which requires pIE->length >= 16.  For WLAN_EID_RSN it compares
  pIE->data + 8, requiring pIE->length >= 12.  Neither requirement
  is checked.

Add the missing IE header and payload bounds checks and guard each
data access with an explicit pIE->length minimum, matching the
pattern established in update_beacon_info().

## References
- https://git.kernel.org/stable/c/204b22c8df115370037248859bf0fa62db73a396
- https://git.kernel.org/stable/c/3bf39f711ff27c64be8680a8938bcc5001982e81
- https://git.kernel.org/stable/c/4380b3860d887a13555ff024a58dfc05b490dfd6
- https://git.kernel.org/stable/c/6f26cc55affd9d7f88ae2f5d12db4ecf9072c209
- https://git.kernel.org/stable/c/a6105ea8ca6ebbc04beaf3bcbf7dbb5985f5d395
- https://git.kernel.org/stable/c/d2055332297e24c63fffda943ef7a5eefc0a6019
- https://git.kernel.org/stable/c/ea3809f7e20bdff282b8cc1e94937d5fb9fb32c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64536.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
