# [H] ftrace: Fix UAF when lookup kallsym after ftrace disabled

## Summary
Severity: High
Advisory: CVE-2025-38346
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38346
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ftrace: Fix UAF when lookup kallsym after ftrace disabled

The following issue happens with a buggy module:

BUG: unable to handle page fault for address: ffffffffc05d0218
PGD 1bd66f067 P4D 1bd66f067 PUD 1bd671067 PMD 101808067 PTE 0
Oops: Oops: 0000 [#1] SMP KASAN PTI
Tainted: [O]=OOT_MODULE, [E]=UNSIGNED_MODULE
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS
RIP: 0010:sized_strscpy+0x81/0x2f0
RSP: 0018:ffff88812d76fa08 EFLAGS: 00010246
RAX: 0000000000000000 RBX: ffffffffc0601010 RCX: dffffc0000000000
RDX: 0000000000000038 RSI: dffffc0000000000 RDI: ffff88812608da2d
RBP: 8080808080808080 R08: ffff88812608da2d R09: ffff88812608da68
R10: ffff88812608d82d R11: ffff88812608d810 R12: 0000000000000038
R13: ffff88812608da2d R14: ffffffffc05d0218 R15: fefefefefefefeff
FS:  00007fef552de740(0000) GS:ffff8884251c7000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: ffffffffc05d0218 CR3: 00000001146f0000 CR4: 00000000000006f0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
Call Trace:
 <TASK>
 ftrace_mod_get_kallsym+0x1ac/0x590
 update_iter_mod+0x239/0x5b0
 s_next+0x5b/0xa0
 seq_read_iter+0x8c9/0x1070
 seq_read+0x249/0x3b0
 proc_reg_read+0x1b0/0x280
 vfs_read+0x17f/0x920
 ksys_read+0xf3/0x1c0
 do_syscall_64+0x5f/0x2e0
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

The above issue may happen as follows:
(1) Add kprobe tracepoint;
(2) insmod test.ko;
(3)  Module triggers ftrace disabled;
(4) rmmod test.ko;
(5) cat /proc/kallsyms; --> Will trigger UAF as test.ko already removed;
ftrace_mod_get_kallsym()
...
strscpy(module_name, mod_map->mod->name, MODULE_NAME_LEN);
...

The problem is when a module triggers an issue with ftrace and
sets ftrace_disable. The ftrace_disable is set when an anomaly is
discovered and to prevent any more damage, ftrace stops all text
modification. The issue that happened was that the ftrace_disable stops
more than just the text modification.

When a module is loaded, its init functions can also be traced. Because
kallsyms deletes the init functions after a module has loaded, ftrace
saves them when the module is loaded and function tracing is enabled. This
allows the output of the function trace to show the init function names
instead of just their raw memory addresses.

When a module is removed, ftrace_release_mod() is called, and if
ftrace_disable is set, it just returns without doing anything more. The
problem here is that it leaves the mod_list still around and if kallsyms
is called, it will call into this code and access the module memory that
has already been freed as it will return:

  strscpy(module_name, mod_map->mod->name, MODULE_NAME_LEN);

Where the "mod" no longer exists and triggers a UAF bug.

## References
- https://git.kernel.org/stable/c/03a162933c4a03b9f1a84f7d8482903c7e1e11bb
- https://git.kernel.org/stable/c/6805582abb720681dd1c87ff677f155dcf4e86c9
- https://git.kernel.org/stable/c/83a692a9792aa86249d68a8ac0b9d55ecdd255fa
- https://git.kernel.org/stable/c/8690cd3258455bbae64f809e1d3ee0f043661c71
- https://git.kernel.org/stable/c/8e89c17dc8970c5f71a3a991f5724d4c8de42d8c
- https://git.kernel.org/stable/c/d064c68781c19f378af1ae741d9132d35d24b2bb
- https://git.kernel.org/stable/c/f78a786ad9a5443a29eef4dae60cde85b7375129
- https://git.kernel.org/stable/c/f914b52c379c12288b7623bb814d0508dbe7481d
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38346.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38346
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
