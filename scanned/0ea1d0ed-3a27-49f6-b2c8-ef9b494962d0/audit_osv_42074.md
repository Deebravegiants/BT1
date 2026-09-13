# [H] staging: rtl8723bs: fix OOB reads in IE loops in issue_assocreq() and join_cmd_hdl()

## Summary
Severity: High
Advisory: CVE-2026-64442
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64442
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: rtl8723bs: fix OOB reads in IE loops in issue_assocreq() and join_cmd_hdl()

Two IE parsing loops are missing the header bounds checks before they
dereference pIE->length:

 - issue_assocreq() walks pmlmeinfo->network.ies to build the
   association request. If the stored IE data ends with only an
   element_id byte and no length byte, pIE->length is read one byte
   past the end of the buffer.

 - join_cmd_hdl() walks pnetwork->ies during station join and has
   the same problem under the same conditions.

Both buffers are filled from AP beacon and probe-response frames, so a
malicious AP that sends a truncated final IE can trigger the issue.

Apply the two-guard pattern established in update_beacon_info():
  1. Break if fewer than sizeof(*pIE) bytes remain.
  2. Break if the IE's declared data extends past the buffer end.

## References
- https://git.kernel.org/stable/c/402f13ec95945f34a210b28df1f8740d3d4a58c5
- https://git.kernel.org/stable/c/4c21eec80cf502d9ea18e0b946246b2376452786
- https://git.kernel.org/stable/c/605ebd94d0f469204f3c9f2f84acc71e43e2780f
- https://git.kernel.org/stable/c/a830bdc82461353bf7b1f8a2ad2689bf5d2de444
- https://git.kernel.org/stable/c/ad2637c46ef8b8ae0894372a2d39fdfcdc420a1e
- https://git.kernel.org/stable/c/bc881c9915c4468747d0ca5fd1abd7b313cfb0f4
- https://git.kernel.org/stable/c/c38d16b1ffac385c9e4b38447cd5c46af1114b58
- https://git.kernel.org/stable/c/ef61d628dfad38fead1fd2e08979ae9126d011d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64442.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64442
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
