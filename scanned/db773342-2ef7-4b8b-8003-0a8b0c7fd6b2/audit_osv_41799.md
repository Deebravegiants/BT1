# [H] thunderbolt: property: Reject u32 wrap in tb_property_entry_valid()

## Summary
Severity: High
Advisory: CVE-2026-63893
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63893
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: property: Reject u32 wrap in tb_property_entry_valid()

entry->value is u32 and entry->length is u16; the sum is performed in
u32 and wraps.  A malicious XDomain peer can pick
value = 0xffffff00, length = 0x100 so the sum 0x100000000 wraps to 0
and passes the > block_len check.  tb_property_parse() then passes
entry->value to parse_dwdata() as a dword offset into the property
block, reading attacker-directed memory far past the allocation.

For TEXT-typed entries with the "deviceid" or "vendorid" keys this
lands in xd->device_name / xd->vendor_name and is readable back via
the per-XDomain device_name / vendor_name sysfs attributes; the leak
is NUL-bounded (kstrdup() stops at the first zero byte) and
untargeted (the attacker picks a delta, not an absolute address).
DATA-typed entries are parsed into property->value.data but not
generically surfaced to userspace.

Use check_add_overflow() so a wrapped sum is rejected.

## References
- https://git.kernel.org/stable/c/01deda0152066c6c955f0619114ea6afa070aaec
- https://git.kernel.org/stable/c/31b98e503ecca8077e5247253dd5425ab84bc96d
- https://git.kernel.org/stable/c/5c06a3043ad944f087bb2ae0aae28d820bb9f460
- https://git.kernel.org/stable/c/6a63623621639acbb39bc2d9fb09559681716695
- https://git.kernel.org/stable/c/8d4a758b407ab3de3be86d1ceadfa35d717d30c7
- https://git.kernel.org/stable/c/9fee50c4e1e42f6d3cbe30df584f9f648f626071
- https://git.kernel.org/stable/c/a47784aee77f33f786dc5d7375db821bdae68792
- https://git.kernel.org/stable/c/e8a0b0a93a6ef958e70b1dd4930beb6dc0026b36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63893.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63893
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
