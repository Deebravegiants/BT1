# [H] tracing/synthetic: Fix races on freeing last_cmd

## Summary
Severity: High
Advisory: CVE-2023-53478
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53478
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/synthetic: Fix races on freeing last_cmd

Currently, the "last_cmd" variable can be accessed by multiple processes
asynchronously when multiple users manipulate synthetic_events node
at the same time, it could lead to use-after-free or double-free.

This patch add "lastcmd_mutex" to prevent "last_cmd" from being accessed
asynchronously.

================================================================

It's easy to reproduce in the KASAN environment by running the two
scripts below in different shells.

script 1:
        while :
        do
                echo -n -e '\x88' > /sys/kernel/tracing/synthetic_events
        done

script 2:
        while :
        do
                echo -n -e '\xb0' > /sys/kernel/tracing/synthetic_events
        done

================================================================
double-free scenario:

    process A                       process B
-------------------               ---------------
1.kstrdup last_cmd
                                  2.free last_cmd
3.free last_cmd(double-free)

================================================================
use-after-free scenario:

    process A                       process B
-------------------               ---------------
1.kstrdup last_cmd
                                  2.free last_cmd
3.tracing_log_err(use-after-free)

================================================================

Appendix 1. KASAN report double-free:

BUG: KASAN: double-free in kfree+0xdc/0x1d4
Free of addr ***** by task sh/4879
Call trace:
        ...
        kfree+0xdc/0x1d4
        create_or_delete_synth_event+0x60/0x1e8
        trace_parse_run_command+0x2bc/0x4b8
        synth_events_write+0x20/0x30
        vfs_write+0x200/0x830
        ...

Allocated by task 4879:
        ...
        kstrdup+0x5c/0x98
        create_or_delete_synth_event+0x6c/0x1e8
        trace_parse_run_command+0x2bc/0x4b8
        synth_events_write+0x20/0x30
        vfs_write+0x200/0x830
        ...

Freed by task 5464:
        ...
        kfree+0xdc/0x1d4
        create_or_delete_synth_event+0x60/0x1e8
        trace_parse_run_command+0x2bc/0x4b8
        synth_events_write+0x20/0x30
        vfs_write+0x200/0x830
        ...

================================================================
Appendix 2. KASAN report use-after-free:

BUG: KASAN: use-after-free in strlen+0x5c/0x7c
Read of size 1 at addr ***** by task sh/5483
sh: CPU: 7 PID: 5483 Comm: sh
        ...
        __asan_report_load1_noabort+0x34/0x44
        strlen+0x5c/0x7c
        tracing_log_err+0x60/0x444
        create_or_delete_synth_event+0xc4/0x204
        trace_parse_run_command+0x2bc/0x4b8
        synth_events_write+0x20/0x30
        vfs_write+0x200/0x830
        ...

Allocated by task 5483:
        ...
        kstrdup+0x5c/0x98
        create_or_delete_synth_event+0x80/0x204
        trace_parse_run_command+0x2bc/0x4b8
        synth_events_write+0x20/0x30
        vfs_write+0x200/0x830
        ...

Freed by task 5480:
        ...
        kfree+0xdc/0x1d4
        create_or_delete_synth_event+0x74/0x204
        trace_parse_run_command+0x2bc/0x4b8
        synth_events_write+0x20/0x30
        vfs_write+0x200/0x830
        ...

## References
- https://git.kernel.org/stable/c/4ccf11c4e8a8e051499d53a12f502196c97a758e
- https://git.kernel.org/stable/c/8826d9e7bd51e7656f78baa4472e8e2f5e7069f0
- https://git.kernel.org/stable/c/9fe183f659a2704255e5d84f6ae308c234a113ec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53478.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
