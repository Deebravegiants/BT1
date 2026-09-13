# [H] net/sched: act_pedit: fix TOCTOU heap OOB write in tc offload

## Summary
Severity: High
Advisory: CVE-2026-72338
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72338
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_pedit: fix TOCTOU heap OOB write in tc offload

There is a TOCTOU race condition in flower lockless approach between sizing
a flow_rule buffer and filling it.
zdi-disclosures@trendmicro.com reports:
The cls_flower classifier operates with TCF_PROTO_OPS_DOIT_UNLOCKED
(fl_change runs without RTNL), while RTM_NEWACTION holds RTNL, so the
independent locking domains make the race reachable in practice.  KASAN
confirms:
  BUG: KASAN: slab-out-of-bounds in tcf_pedit_offload_act_setup+0x81b/0x930
  Write of size 4 at addr ffff888001f27520 by task poc-toctou/312
  The buggy address is located 0 bytes to the right of
   allocated 288-byte region [ffff888001f27400, ffff888001f27520)
   (cache kmalloc-512)

Note: The result is a heap OOB write attacker-controlled content into the
adjacent slab object (requires CAP_NET_ADMIN).

The fix introduces reading tcfp_nkeys under act->tcfa_lock in all places
using a new tcf_pedit_nkeys_locked() which replaces the old tcf_pedit_nkeys().
Additionally we close the remaining TOCTOU window between the sizing read and
the fill reads by more careful accounting.
Rather than silently truncating the key count, which leads to incorrect
action semantics offloaded to hardware and secondary OOB writes if
the remaining capacity is zero or consumed by prior actions, we enforce
remaining capacity checks and return -ENOSPC if the required space exceeds
the remaining capacity.

## References
- https://git.kernel.org/stable/c/0d8532a5e972a5351cf4ee4a435e0d65cbba8f23
- https://git.kernel.org/stable/c/27488e1a7f19757e6146edca9458ed4ffc545557
- https://git.kernel.org/stable/c/6f9b23eb92a894ae1118893996943990ee0b860e
- https://git.kernel.org/stable/c/8b519cbcabe836a441369fbec1a8a6518a709251
- https://git.kernel.org/stable/c/8e49cd891bda447c68122d672510a604a8bb6b24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72338.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72338
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
