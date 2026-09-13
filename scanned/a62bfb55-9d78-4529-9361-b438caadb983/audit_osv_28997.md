# [H] ftrace: Fix possible use-after-free issue in ftrace_location()

## Summary
Severity: High
Advisory: CVE-2024-38588
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38588
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.4.286, >=5.5.0 <5.10.227, >=5.11.0 <5.15.162, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ftrace: Fix possible use-after-free issue in ftrace_location()

KASAN reports a bug:

  BUG: KASAN: use-after-free in ftrace_location+0x90/0x120
  Read of size 8 at addr ffff888141d40010 by task insmod/424
  CPU: 8 PID: 424 Comm: insmod Tainted: G        W          6.9.0-rc2+
  [...]
  Call Trace:
   <TASK>
   dump_stack_lvl+0x68/0xa0
   print_report+0xcf/0x610
   kasan_report+0xb5/0xe0
   ftrace_location+0x90/0x120
   register_kprobe+0x14b/0xa40
   kprobe_init+0x2d/0xff0 [kprobe_example]
   do_one_initcall+0x8f/0x2d0
   do_init_module+0x13a/0x3c0
   load_module+0x3082/0x33d0
   init_module_from_file+0xd2/0x130
   __x64_sys_finit_module+0x306/0x440
   do_syscall_64+0x68/0x140
   entry_SYSCALL_64_after_hwframe+0x71/0x79

The root cause is that, in lookup_rec(), ftrace record of some address
is being searched in ftrace pages of some module, but those ftrace pages
at the same time is being freed in ftrace_release_mod() as the
corresponding module is being deleted:

           CPU1                       |      CPU2
  register_kprobes() {                | delete_module() {
    check_kprobe_address_safe() {     |
      arch_check_ftrace_location() {  |
        ftrace_location() {           |
          lookup_rec() // USE!        |   ftrace_release_mod() // Free!

To fix this issue:
  1. Hold rcu lock as accessing ftrace pages in ftrace_location_range();
  2. Use ftrace_location_range() instead of lookup_rec() in
     ftrace_location();
  3. Call synchronize_rcu() before freeing any ftrace pages both in
     ftrace_process_locs()/ftrace_release_mod()/ftrace_free_mem().

## References
- https://git.kernel.org/stable/c/1880a324af1c95940a7c954b6b937e86844a33bd
- https://git.kernel.org/stable/c/31310e373f4c8c74e029d4326b283e757edabc0b
- https://git.kernel.org/stable/c/66df065b3106964e667b37bf8f7e55ec69d0c1f6
- https://git.kernel.org/stable/c/7b4881da5b19f65709f5c18c1a4d8caa2e496461
- https://git.kernel.org/stable/c/8ea8ef5e42173560ac510e92a1cc797ffeea8831
- https://git.kernel.org/stable/c/dbff5f0bfb2416b8b55c105ddbcd4f885e98fada
- https://git.kernel.org/stable/c/e60b613df8b6253def41215402f72986fee3fc8d
- https://git.kernel.org/stable/c/eea46baf145150910ba134f75a67106ba2222c1b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38588.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38588
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
