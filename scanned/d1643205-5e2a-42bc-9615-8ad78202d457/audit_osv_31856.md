# [H] perf/core: Add RCU read lock protection to perf_iterate_ctx()

## Summary
Severity: High
Advisory: CVE-2025-21889
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-21889
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.81, >=6.7.0 <6.12.18, >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/core: Add RCU read lock protection to perf_iterate_ctx()

The perf_iterate_ctx() function performs RCU list traversal but
currently lacks RCU read lock protection. This causes lockdep warnings
when running perf probe with unshare(1) under CONFIG_PROVE_RCU_LIST=y:

	WARNING: suspicious RCU usage
	kernel/events/core.c:8168 RCU-list traversed in non-reader section!!

	 Call Trace:
	  lockdep_rcu_suspicious
	  ? perf_event_addr_filters_apply
	  perf_iterate_ctx
	  perf_event_exec
	  begin_new_exec
	  ? load_elf_phdrs
	  load_elf_binary
	  ? lock_acquire
	  ? find_held_lock
	  ? bprm_execve
	  bprm_execve
	  do_execveat_common.isra.0
	  __x64_sys_execve
	  do_syscall_64
	  entry_SYSCALL_64_after_hwframe

This protection was previously present but was removed in commit
bd2756811766 ("perf: Rewrite core context handling"). Add back the
necessary rcu_read_lock()/rcu_read_unlock() pair around
perf_iterate_ctx() call in perf_event_exec().

[ mingo: Use scoped_guard() as suggested by Peter ]

## References
- https://git.kernel.org/stable/c/0fe8813baf4b2e865d3b2c735ce1a15b86002c74
- https://git.kernel.org/stable/c/a2475ccad6120546ea45dbcd6cd1f74dc565ef6b
- https://git.kernel.org/stable/c/dd536566dda9a551fc2a2acfab5313a5bb13ed02
- https://git.kernel.org/stable/c/f390c2eea571945f357a2d3b9fcb1c015767132e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21889.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21889
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
