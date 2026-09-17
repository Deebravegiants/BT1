# [H] xfrm: state: initialize state_ptrs earlier in xfrm_state_find

## Summary
Severity: High
Advisory: CVE-2025-38675
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38675
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.41, >=6.13.0 <6.15.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: state: initialize state_ptrs earlier in xfrm_state_find

In case of preemption, xfrm_state_look_at will find a different
pcpu_id and look up states for that other CPU. If we matched a state
for CPU2 in the state_cache while the lookup started on CPU1, we will
jump to "found", but the "best" state that we got will be ignored and
we will enter the "acquire" block. This block uses state_ptrs, which
isn't initialized at this point.

Let's initialize state_ptrs just after taking rcu_read_lock. This will
also prevent a possible misuse in the future, if someone adjusts this
function.

## References
- https://git.kernel.org/stable/c/463562f9591742be62ddde3b426a0533ed496955
- https://git.kernel.org/stable/c/6bf2daafc51bcb9272c0fdff2afd38217337d0d3
- https://git.kernel.org/stable/c/94d077c331730510d5611b438640a292097341f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38675.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38675
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
