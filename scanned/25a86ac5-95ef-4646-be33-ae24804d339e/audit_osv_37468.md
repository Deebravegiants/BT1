# [H] btrfs: fix incorrect return value after changing leaf in lookup_extent_data_ref()

## Summary
Severity: High
Advisory: CVE-2026-31666
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31666
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix incorrect return value after changing leaf in lookup_extent_data_ref()

After commit 1618aa3c2e01 ("btrfs: simplify return variables in
lookup_extent_data_ref()"), the err and ret variables were merged into
a single ret variable. However, when btrfs_next_leaf() returns 0
(success), ret is overwritten from -ENOENT to 0. If the first key in
the next leaf does not match (different objectid or type), the function
returns 0 instead of -ENOENT, making the caller believe the lookup
succeeded when it did not. This can lead to operations on the wrong
extent tree item, potentially causing extent tree corruption.

Fix this by returning -ENOENT directly when the key does not match,
instead of relying on the ret variable.

## References
- https://git.kernel.org/stable/c/316fb1b3169efb081d2db910cbbfef445afa03b9
- https://git.kernel.org/stable/c/4125a194db4a6cf91f619f38788272651cb97dce
- https://git.kernel.org/stable/c/450e6a685d0cad95b15f8af152057bd0bf79f50b
- https://git.kernel.org/stable/c/ab1e022379c3c811aa72da8eb0c7507859a1d0f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31666.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31666
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
