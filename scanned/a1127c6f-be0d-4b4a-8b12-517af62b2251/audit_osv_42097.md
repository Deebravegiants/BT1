# [H] wifi: mac80211: fix MLE defragmentation

## Summary
Severity: High
Advisory: CVE-2026-64515
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64515
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix MLE defragmentation

If either reconf or EPCS multi-link element (MLE) is contained in
a non-transmitted profile, the defragmentation routine is called
with a pointer to the defragmented copy, but the original elements.

This is incorrect for two reasons:
 - if the original defragmentation was needed, it will not find the
   correct data
 - if the original frame is at a higher address, the parsing will
   potentially overrun the heap data (though given the layout of
   the buffers, only into the new defragmentation buffer, and then
   it has to stop and fail once that's filled with copied data.

Fix it by tracking the container along with the pointer and in
doing so also unify the two almost identical defragmentation
routines.

## References
- https://git.kernel.org/stable/c/1f573e17bcb7275ddd1c8f47f46ae0faf0e902a4
- https://git.kernel.org/stable/c/55c479aae99b120489a432db9c717484e523dfd6
- https://git.kernel.org/stable/c/722b3f86df80644463d29fe5451e30a617f74500
- https://git.kernel.org/stable/c/a74e893f30db64cdce0fc7a96d3baa417bcd55f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64515.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64515
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
