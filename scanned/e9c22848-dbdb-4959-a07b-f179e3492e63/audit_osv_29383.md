# [H] filemap: replace pte_offset_map() with pte_offset_map_nolock()

## Summary
Severity: High
Advisory: CVE-2024-42233
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42233
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

filemap: replace pte_offset_map() with pte_offset_map_nolock()

The vmf->ptl in filemap_fault_recheck_pte_none() is still set from
handle_pte_fault().  But at the same time, we did a pte_unmap(vmf->pte). 
After a pte_unmap(vmf->pte) unmap and rcu_read_unlock(), the page table
may be racily changed and vmf->ptl maybe fails to protect the actual page
table.  Fix this by replacing pte_offset_map() with
pte_offset_map_nolock().

As David said, the PTL pointer might be stale so if we continue to use
it infilemap_fault_recheck_pte_none(), it might trigger UAF.  Also, if
the PTL fails, the issue fixed by commit 58f327f2ce80 ("filemap: avoid
unnecessary major faults in filemap_fault()") might reappear.

## References
- https://git.kernel.org/stable/c/24be02a42181f0707be0498045c4c4b13273b16d
- https://git.kernel.org/stable/c/6a6c2aec1a89506595801b4cf7e8eef035f33748
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42233.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42233
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
