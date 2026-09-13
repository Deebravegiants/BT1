# [H] apparmor: fix side-effect bug in match_char() macro usage

## Summary
Severity: High
Advisory: CVE-2026-23406
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-23406
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.18, >=6.19.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: fix side-effect bug in match_char() macro usage

The match_char() macro evaluates its character parameter multiple
times when traversing differential encoding chains. When invoked
with *str++, the string pointer advances on each iteration of the
inner do-while loop, causing the DFA to check different characters
at each iteration and therefore skip input characters.
This results in out-of-bounds reads when the pointer advances past
the input buffer boundary.

[   94.984676] ==================================================================
[   94.985301] BUG: KASAN: slab-out-of-bounds in aa_dfa_match+0x5ae/0x760
[   94.985655] Read of size 1 at addr ffff888100342000 by task file/976

[   94.986319] CPU: 7 UID: 1000 PID: 976 Comm: file Not tainted 6.19.0-rc7-next-20260127 #1 PREEMPT(lazy)
[   94.986322] Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
[   94.986329] Call Trace:
[   94.986341]  <TASK>
[   94.986347]  dump_stack_lvl+0x5e/0x80
[   94.986374]  print_report+0xc8/0x270
[   94.986384]  ? aa_dfa_match+0x5ae/0x760
[   94.986388]  kasan_report+0x118/0x150
[   94.986401]  ? aa_dfa_match+0x5ae/0x760
[   94.986405]  aa_dfa_match+0x5ae/0x760
[   94.986408]  __aa_path_perm+0x131/0x400
[   94.986418]  aa_path_perm+0x219/0x2f0
[   94.986424]  apparmor_file_open+0x345/0x570
[   94.986431]  security_file_open+0x5c/0x140
[   94.986442]  do_dentry_open+0x2f6/0x1120
[   94.986450]  vfs_open+0x38/0x2b0
[   94.986453]  ? may_open+0x1e2/0x2b0
[   94.986466]  path_openat+0x231b/0x2b30
[   94.986469]  ? __x64_sys_openat+0xf8/0x130
[   94.986477]  do_file_open+0x19d/0x360
[   94.986487]  do_sys_openat2+0x98/0x100
[   94.986491]  __x64_sys_openat+0xf8/0x130
[   94.986499]  do_syscall_64+0x8e/0x660
[   94.986515]  ? count_memcg_events+0x15f/0x3c0
[   94.986526]  ? srso_alias_return_thunk+0x5/0xfbef5
[   94.986540]  ? handle_mm_fault+0x1639/0x1ef0
[   94.986551]  ? vma_start_read+0xf0/0x320
[   94.986558]  ? srso_alias_return_thunk+0x5/0xfbef5
[   94.986561]  ? srso_alias_return_thunk+0x5/0xfbef5
[   94.986563]  ? fpregs_assert_state_consistent+0x50/0xe0
[   94.986572]  ? srso_alias_return_thunk+0x5/0xfbef5
[   94.986574]  ? arch_exit_to_user_mode_prepare+0x9/0xb0
[   94.986587]  ? srso_alias_return_thunk+0x5/0xfbef5
[   94.986588]  ? irqentry_exit+0x3c/0x590
[   94.986595]  entry_SYSCALL_64_after_hwframe+0x76/0x7e
[   94.986597] RIP: 0033:0x7fda4a79c3ea

Fix by extracting the character value before invoking match_char,
ensuring single evaluation per outer loop.

## References
- https://git.kernel.org/stable/c/0510d1ba0976f97f521feb2b75b0572ea5df3ceb
- https://git.kernel.org/stable/c/1fc94f16098213d01e56c97feed9b3ecf0147a37
- https://git.kernel.org/stable/c/383b7270faf42564f133134c2fc3c24bbae52615
- https://git.kernel.org/stable/c/5a184f7cbdeaad17e16dedf3c17d0cd622edfed8
- https://git.kernel.org/stable/c/8756b68edae37ff546c02091989a4ceab3f20abd
- https://git.kernel.org/stable/c/b73c1dff8a9d7eeaebabf8097a5b2de192f40913
- https://git.kernel.org/stable/c/c7dc56d8b37eda1396feeec3ab1c7ecee5eae31b
- https://git.kernel.org/stable/c/f16f2e5936c0f5f0d11fdf10d2be3e47e7108e42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23406
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
