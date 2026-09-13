# [H] staging: rtl8723bs: fix WEP length underflow and OOB read in OnAuth()

## Summary
Severity: High
Advisory: CVE-2026-64445
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64445
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix WEP length underflow and OOB read in OnAuth()

OnAuth() has two bugs in the shared-key authentication path.

When the Privacy bit is set, rtw_wep_decrypt() is called without
verifying that the frame is long enough to contain a valid WEP IV and
ICV.  Inside rtw_wep_decrypt(), length is computed as:

    length = len - WLAN_HDR_A3_LEN - iv_len

and then passed as (length - 4) to crc32_le().  If len is less than
WLAN_HDR_A3_LEN + iv_len + icv_len (32 bytes), length - 4 is negative
and, after the implicit cast to size_t, causes crc32_le() to read far
beyond the frame buffer.  Add a minimum length check before accessing
the IV field and calling the decryption path.

When processing a seq=3 response, rtw_get_ie() stores the Challenge
Text IE length in ie_len, but the subsequent memcmp() always reads 128
bytes regardless of ie_len.  IEEE 802.11 mandates a challenge text of
exactly 128 bytes; reject any IE whose length field differs, matching
the check already applied to OnAuthClient().

## References
- https://git.kernel.org/stable/c/1f6c9d255bdda41216b6e34c96aa2b1abee0bb84
- https://git.kernel.org/stable/c/3e44a7665f3abd320a80d9c64ee4a93317041b8b
- https://git.kernel.org/stable/c/64ec4192d9c10e96922245d4a6747304cc76b19d
- https://git.kernel.org/stable/c/665e1ecb68b4e8419604e70a33f02d1c8b0222c6
- https://git.kernel.org/stable/c/87cccc2a767f17dcab71e3b9fe5ae29b5516c5ce
- https://git.kernel.org/stable/c/a1fc19d61f661d47204f095b593de507884849f7
- https://git.kernel.org/stable/c/c9000c93078e5c0a5a651b077c0ec92a4bc7d580
- https://git.kernel.org/stable/c/d90b9f39f375c9826ef145605dfe97765d0ecb91
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64445.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64445
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
