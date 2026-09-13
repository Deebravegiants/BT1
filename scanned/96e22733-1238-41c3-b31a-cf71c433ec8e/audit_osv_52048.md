# [M] CVE-2021-47006

## Summary
Severity: Medium
Advisory: CVE-2021-47006
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47006
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: 9064/1: hw_breakpoint: Do not directly check the event's overflow_handler hook

The commit 1879445dfa7b ("perf/core: Set event's default
::overflow_handler()") set a default event->overflow_handler in
perf_event_alloc(), and replace the check event->overflow_handler with
is_default_overflow_handler(), but one is missing.

Currently, the bp->overflow_handler can not be NULL. As a result,
enable_single_step() is always not invoked.

Comments from Zhen Lei:

 https://patchwork.kernel.org/project/linux-arm-kernel/patch/20210207105934.2001-1-thunder.leizhen@huawei.com/

## References
- https://git.kernel.org/stable/c/dabe299425b1a53a69461fed7ac8922ea6733a25
- https://git.kernel.org/stable/c/ed1f67465327cec4457bb988775245b199da86e6
- https://git.kernel.org/stable/c/3ed8832aeaa9a37b0fc386bb72ff604352567c80
- https://git.kernel.org/stable/c/555a70f7fff03bd669123487905c47ae27dbdaac
- https://git.kernel.org/stable/c/630146203108bf6b8934eec0dfdb3e46dcb917de
- https://git.kernel.org/stable/c/7eeacc6728c5478e3c01bc82a1f08958eaa12366
- https://git.kernel.org/stable/c/a506bd5756290821a4314f502b4bafc2afcf5260
- https://git.kernel.org/stable/c/a9938d6d78a238d6ab8de57a4d3dcf77adceb9bb
