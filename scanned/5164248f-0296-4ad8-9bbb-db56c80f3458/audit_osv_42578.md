# [H] device property: initialize the remaining fields of fwnode_handle in fwnode_init()

## Summary
Severity: High
Advisory: CVE-2026-68461
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68461
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

device property: initialize the remaining fields of fwnode_handle in fwnode_init()

If a firmware node is allocated on the stack (for instance: temporary
software node whose life-time we control) or on the heap - but using a
non-zeroing allocation function - and initialized using fwnode_init(),
its secondary pointer will contain uninitialized memory which likely
will be neither NULL nor IS_ERR() and so may end up being dereferenced
(for example: in dev_to_swnode()). Set fwnode->secondary to NULL on
initialization. While at it: initialize the remaining fields of struct
fwnode_handle too just to be sure.

[ Fix typo in commit message. - Danilo ]

## References
- https://git.kernel.org/stable/c/0198d579948322cda5178b9672d448375a32f947
- https://git.kernel.org/stable/c/173b61c9276c7b3a5fbcc63ae7aafc897fee1e18
- https://git.kernel.org/stable/c/7eba000621fff223dd7bab484d48918c7c77a307
- https://git.kernel.org/stable/c/9c86a1f930bb2ddb85f867b4736716e82a4a4683
- https://git.kernel.org/stable/c/c81e2af41de6a159837c7129a4fc444ac6e48046
- https://git.kernel.org/stable/c/c8542b68ba6ef4f61072098893a3f5b71c569b6c
- https://git.kernel.org/stable/c/f0b4e1cc8ad76baf49d898727eb52e91a4ef0544
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68461.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68461
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
