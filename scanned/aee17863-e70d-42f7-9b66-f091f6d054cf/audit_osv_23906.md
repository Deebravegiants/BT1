# [M] tracing/histograms: Fix memory leak problem

## Summary
Severity: Medium
Advisory: CVE-2022-49648
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49648
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.132, >=5.9.0 <5.15.56, >=5.11.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/histograms: Fix memory leak problem

This reverts commit 46bbe5c671e06f070428b9be142cc4ee5cedebac.

As commit 46bbe5c671e0 ("tracing: fix double free") said, the
"double free" problem reported by clang static analyzer is:
  > In parse_var_defs() if there is a problem allocating
  > var_defs.expr, the earlier var_defs.name is freed.
  > This free is duplicated by free_var_defs() which frees
  > the rest of the list.

However, if there is a problem allocating N-th var_defs.expr:
  + in parse_var_defs(), the freed 'earlier var_defs.name' is
    actually the N-th var_defs.name;
  + then in free_var_defs(), the names from 0th to (N-1)-th are freed;

                        IF ALLOCATING PROBLEM HAPPENED HERE!!! -+
                                                                 \
                                                                  |
          0th           1th                 (N-1)-th      N-th    V
          +-------------+-------------+-----+-------------+-----------
var_defs: | name | expr | name | expr | ... | name | expr | name | ///
          +-------------+-------------+-----+-------------+-----------

These two frees don't act on same name, so there was no "double free"
problem before. Conversely, after that commit, we get a "memory leak"
problem because the above "N-th var_defs.name" is not freed.

If enable CONFIG_DEBUG_KMEMLEAK and inject a fault at where the N-th
var_defs.expr allocated, then execute on shell like:
  $ echo 'hist:key=call_site:val=$v1,$v2:v1=bytes_req,v2=bytes_alloc' > \
/sys/kernel/debug/tracing/events/kmem/kmalloc/trigger

Then kmemleak reports:
  unreferenced object 0xffff8fb100ef3518 (size 8):
    comm "bash", pid 196, jiffies 4295681690 (age 28.538s)
    hex dump (first 8 bytes):
      76 31 00 00 b1 8f ff ff                          v1......
    backtrace:
      [<0000000038fe4895>] kstrdup+0x2d/0x60
      [<00000000c99c049a>] event_hist_trigger_parse+0x206f/0x20e0
      [<00000000ae70d2cc>] trigger_process_regex+0xc0/0x110
      [<0000000066737a4c>] event_trigger_write+0x75/0xd0
      [<000000007341e40c>] vfs_write+0xbb/0x2a0
      [<0000000087fde4c2>] ksys_write+0x59/0xd0
      [<00000000581e9cdf>] do_syscall_64+0x3a/0x80
      [<00000000cf3b065c>] entry_SYSCALL_64_after_hwframe+0x46/0xb0

## References
- https://git.kernel.org/stable/c/22eeff55679d9e7c0f768c79bfbd83e2f8142d89
- https://git.kernel.org/stable/c/4d453eb5e1eec89971aa5b3262857ee26cfdffd3
- https://git.kernel.org/stable/c/78a1400c42ee11197eb1f0f85ba51df9a4fdfff0
- https://git.kernel.org/stable/c/7edc3945bdce9c39198a10d6129377a5c53559c2
- https://git.kernel.org/stable/c/eb622d5580b9e2ff694f62da6410618bd73853cb
- https://git.kernel.org/stable/c/ecc6dec12c33aa92c086cd702af9f544ddaf3c75
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49648.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49648
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
