# [H] tracing/probes: Fix MAX_TRACE_ARGS limit handling

## Summary
Severity: High
Advisory: CVE-2024-50132
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50132
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing/probes: Fix MAX_TRACE_ARGS limit handling

When creating a trace_probe we would set nr_args prior to truncating the
arguments to MAX_TRACE_ARGS. However, we would only initialize arguments
up to the limit.

This caused invalid memory access when attempting to set up probes with
more than 128 fetchargs.

  BUG: kernel NULL pointer dereference, address: 0000000000000020
  #PF: supervisor read access in kernel mode
  #PF: error_code(0x0000) - not-present page
  PGD 0 P4D 0
  Oops: Oops: 0000 [#1] PREEMPT SMP PTI
  CPU: 0 UID: 0 PID: 1769 Comm: cat Not tainted 6.11.0-rc7+ #8
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-1.fc39 04/01/2014
  RIP: 0010:__set_print_fmt+0x134/0x330

Resolve the issue by applying the MAX_TRACE_ARGS limit earlier. Return
an error when there are too many arguments instead of silently
truncating.

## References
- https://git.kernel.org/stable/c/08ccd1a57c4d3882e9a877eb2dcc66e50a3b0279
- https://git.kernel.org/stable/c/6bc24db74fe4788cc7c2f30a113fc6aafba225a3
- https://git.kernel.org/stable/c/73f35080477e893aa6f4c8d388352b871b288fbc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50132.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50132
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
