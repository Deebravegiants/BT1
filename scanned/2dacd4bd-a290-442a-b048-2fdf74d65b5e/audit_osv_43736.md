# [H] staging: rtl8723bs: fix OOB read in rtw_get_wpa_ie()

## Summary
Severity: High
Advisory: CVE-2026-74651
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74651
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix OOB read in rtw_get_wpa_ie()

rtw_get_wpa_ie() reads bytes at fixed offsets into a vendor-specific
information element without checking that the element is long enough,
causing an out-of-bounds read for a short trailing IE.

The function locates a vendor-specific IE (EID 221) with rtw_get_ie()
and then compares a 4-byte OUI+type at pbuf + 2 and reads a 2-byte
version word at pbuf + 6. Those accesses require the IE body to be at
least 6 bytes, but rtw_get_ie() only guarantees that the element fits
within the buffer; it does not enforce a minimum body length. A
vendor-specific IE whose length byte is 0 to 5, placed at the end of
the buffer, therefore makes these reads run past the end of the IE and
past the end of the buffer itself.

The buffer holds information elements taken from received management
frames and from the IE blob passed to rtw_cfg80211_set_wpa_ie(), which
is kmemdup'd to its exact length, so the read can run off the end of
the allocation.

The sibling helpers rtw_get_sec_ie(), rtw_get_wapi_ie() and
rtw_get_wps_ie() in this file already reject too-short vendor-specific
IEs before their OUI memcmp(); rtw_get_wpa_ie() was never brought in
line with them, and needs a minimum of 6 rather than 4 bytes because
of the version word. Add the missing length check.

## References
- https://git.kernel.org/stable/c/01ab275f8f3e497a13ebbe4ded44ec0623bccde3
- https://git.kernel.org/stable/c/0d19f0600fbb610c42f2a86f95c35706dc04691b
- https://git.kernel.org/stable/c/1c3e23e78862493e8cf1adad02b10ffcb8b9921c
- https://git.kernel.org/stable/c/42c5a0d454aa5b54fec17162d9a1f8c30f8af45a
- https://git.kernel.org/stable/c/4fc459c5cd8767ca4d9bf2f7becbd562639ba4d9
- https://git.kernel.org/stable/c/b45be82387bf759931acdd21ca7dfe740f16eb97
- https://git.kernel.org/stable/c/c9068f82a0906b29c905e8788edb62c3208c7c8a
- https://git.kernel.org/stable/c/e167a38a8a8f50f137721fef1a1fbba0f4588b5d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74651.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74651
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
