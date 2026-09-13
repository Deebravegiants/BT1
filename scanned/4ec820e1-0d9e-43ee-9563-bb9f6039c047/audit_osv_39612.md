# [H] of: unittest: fix use-after-free in of_unittest_changeset()

## Summary
Severity: High
Advisory: CVE-2026-46288
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46288
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

of: unittest: fix use-after-free in of_unittest_changeset()

The variable 'parent' is assigned the value of 'nchangeset' earlier in the
function, meaning both point to the same struct device_node. The call to
of_node_put(nchangeset) can decrement the reference count to zero and
free the node if there are no other holders. After that, the code still
uses 'parent' to check for the presence of a property and to read a
string property, leading to a use-after-free.

Fix this by moving the of_node_put() call after the last access to
'parent', avoiding the UAF.

## References
- https://git.kernel.org/stable/c/37318d1a27c9cc5a70d3cd7e49e30ec86f2b8ca1
- https://git.kernel.org/stable/c/6fdad20b7975bdc32e85b45f8f7c640f6687b81f
- https://git.kernel.org/stable/c/7f0f0926f3010b10cff5e93446258f971e42f2fd
- https://git.kernel.org/stable/c/faecdd423c27f0d6090156a435ba9dbbac0eaddb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46288.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
