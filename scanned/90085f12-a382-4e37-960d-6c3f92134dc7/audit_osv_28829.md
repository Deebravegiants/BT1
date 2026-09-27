# [M] blk-iocost: avoid out of bounds shift

## Summary
Severity: Medium
Advisory: CVE-2024-36916
Ecosystem: Linux
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36916
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-iocost: avoid out of bounds shift

UBSAN catches undefined behavior in blk-iocost, where sometimes
iocg->delay is shifted right by a number that is too large,
resulting in undefined behavior on some architectures.

[  186.556576] ------------[ cut here ]------------
UBSAN: shift-out-of-bounds in block/blk-iocost.c:1366:23
shift exponent 64 is too large for 64-bit type 'u64' (aka 'unsigned long long')
CPU: 16 PID: 0 Comm: swapper/16 Tainted: G S          E    N 6.9.0-0_fbk700_debug_rc2_kbuilder_0_gc85af715cac0 #1
Hardware name: Quanta Twin Lakes MP/Twin Lakes Passive MP, BIOS F09_3A23 12/08/2020
Call Trace:
 <IRQ>
 dump_stack_lvl+0x8f/0xe0
 __ubsan_handle_shift_out_of_bounds+0x22c/0x280
 iocg_kick_delay+0x30b/0x310
 ioc_timer_fn+0x2fb/0x1f80
 __run_timer_base+0x1b6/0x250
...

Avoid that undefined behavior by simply taking the
"delay = 0" branch if the shift is too large.

I am not sure what the symptoms of an undefined value
delay will be, but I suspect it could be more than a
little annoying to debug.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/488dc6808cb8369685f18cee81e88e7052ac153b
- https://git.kernel.org/stable/c/62accf6c1d7b433752cb3591bba8967b7a801ad5
- https://git.kernel.org/stable/c/844fc023e9f14a4fb1de5ae1eaefafd6d69c5fa1
- https://git.kernel.org/stable/c/beaa51b36012fad5a4d3c18b88a617aea7a9b96d
- https://git.kernel.org/stable/c/ce0e99cae00e3131872936713b7f55eefd53ab86
- https://git.kernel.org/stable/c/f6add0a6f78dc6360b822ca4b6f9f2f14174c8ca
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36916.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36916
- https://security.netapp.com/advisory/ntap-20240905-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
