# [H] staging: rtl8723bs: fix OOB write in HT_caps_handler()

## Summary
Severity: High
Advisory: CVE-2026-64440
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64440
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix OOB write in HT_caps_handler()

HT_caps_handler() iterates pIE->length bytes and writes into
HT_caps.u.HT_cap[], which is a fixed 26-byte array (sizeof struct
HT_caps_element). Because pIE->length is a raw u8 from an over-the-air
802.11 AssocResponse frame and is never validated, a malicious AP can
set it up to 255, causing up to 229 bytes of out-of-bounds writes into
adjacent fields of struct mlme_ext_info.

Truncate the iteration count to the size of HT_caps.u.HT_cap using
umin() so that data from a longer-than-expected IE is silently ignored
rather than written out of bounds, preserving interoperability with APs
that pad the element. An early return on oversized IEs was considered
but rejected: it would bypass the pmlmeinfo->HT_caps_enable = 1
assignment that precedes the loop, silently disabling HT mode for APs
that append extra bytes to the HT Capabilities IE.

## References
- https://git.kernel.org/stable/c/225b6d3fc7e99ac3d20b6c861d1e47d24e7ea31d
- https://git.kernel.org/stable/c/37f642d47c3648a707df3ceb092eee1adffbfd28
- https://git.kernel.org/stable/c/6f91621fc45025ad3c0be796b70e6e4cee22fc69
- https://git.kernel.org/stable/c/8c872b47c7fc32e95e0da1db7512388794adcd69
- https://git.kernel.org/stable/c/918537a0fbed85aab61fa28ad75e6279070610c9
- https://git.kernel.org/stable/c/bb3b942da4123b55d1cacf19d1a7d5ba15dbf83a
- https://git.kernel.org/stable/c/f8001e1a516ba3b495728c65b61f799cbfad6bd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64440.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
