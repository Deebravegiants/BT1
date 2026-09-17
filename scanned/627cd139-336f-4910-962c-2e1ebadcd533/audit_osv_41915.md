# [C] batman-adv: tt: fix negative last_changeset_len

## Summary
Severity: Critical
Advisory: CVE-2026-64089
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64089
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: tt: fix negative last_changeset_len

batadv_piv_tt::last_changeset_len len was declared as s16, but the field is
never intended to hold a negative value. When a value greater than 32767 is
assigned, it wraps to a negative signed integer.

In batadv_send_my_tt_response(), last_changeset_len is temporarily widened
to s32. The incorrectly negative s16 value propagates into the s32, causing
batadv_tt_prepare_tvlv_local_data() to allocate a full sized buffer but
populates only a small portion of it with the collected changeset. All
remaining bits are kept uninitialized.

Using an u16 avoids this type confusion and ensures that no (negative) sign
extension is performed in batadv_send_my_tt_response().

## References
- https://git.kernel.org/stable/c/179eb62506a02d00370bd6478898cb632e10986c
- https://git.kernel.org/stable/c/22d59c72f4a47ffec121d0610f70d0d70c3c11c8
- https://git.kernel.org/stable/c/55dc41fe8821e9a849e147255ad572bc933a9d15
- https://git.kernel.org/stable/c/6314089acf0ddf64376fdc0b1420695504c73f52
- https://git.kernel.org/stable/c/c424e8519ac78eac5d9f4eecf06208a0d619ec14
- https://git.kernel.org/stable/c/d29abf70c665730e249d2ec8e1402095ae26bcee
- https://git.kernel.org/stable/c/eb235472b52ef36981c5aad330485eaf2382c53b
- https://git.kernel.org/stable/c/fc92cdfcb295cefa4344d71a527d61b638b7bfc4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64089.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64089
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
