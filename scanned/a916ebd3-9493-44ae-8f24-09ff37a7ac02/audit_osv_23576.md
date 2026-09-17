# [M] rtc: gamecube: Fix refcount leak in gamecube_rtc_read_offset_from_sram

## Summary
Severity: Medium
Advisory: CVE-2022-49150
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49150
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtc: gamecube: Fix refcount leak in gamecube_rtc_read_offset_from_sram

The of_find_compatible_node() function returns a node pointer with
refcount incremented, We should use of_node_put() on it when done
Add the missing of_node_put() to release the refcount.

## References
- https://git.kernel.org/stable/c/4b2dc39ca024990abe36ad5d145c4fe0c06afd34
- https://git.kernel.org/stable/c/de66e4f28dfd11f954966c447b4430529ed040a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49150.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49150
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
