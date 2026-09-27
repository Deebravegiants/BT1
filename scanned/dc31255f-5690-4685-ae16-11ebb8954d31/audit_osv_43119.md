# [H] soundwire: fix bug in sdw_add_element_group_count found by syzkaller

## Summary
Severity: High
Advisory: CVE-2026-72488
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72488
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

soundwire: fix bug in sdw_add_element_group_count found by syzkaller

The original implementation caused an out-of-bounds memory access
in the sdw_add_element_group_count for-loop when i == num.

for (i = 0; i <= num; i++) {
    if (rate == group->rates[i] && lane == group->lanes[i])
        ...

To fix this error, the function now checks for existing rate/lane
entries in the group(a function parameter) using a for-loop before
adding them.

No functional changes apart from this fix.

## References
- https://git.kernel.org/stable/c/a454f61747c97e2eadaa7a35ffc1f4b1645c6a53
- https://git.kernel.org/stable/c/e483a406a23a92d5202e8d324f206e127eef48ff
- https://git.kernel.org/stable/c/f772ff5a0e6758fd412803c09e03ba3bca5f5878
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72488.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72488
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
