# [H] openrisc: signal: do not restore privileged SR bits on sigreturn

## Summary
Severity: High
Advisory: CVE-2026-80560
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80560
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

openrisc: signal: do not restore privileged SR bits on sigreturn

restore_sigcontext() copies the whole supervision register (SR) from the
signal frame and only clears SPR_SR_SM before the value is reloaded into
the hardware SR (through ESR and l.rfe) on the return to user space.  All
other SR bits are left under user control.

An unprivileged task can thus return from a signal handler through a
crafted sigframe that clears SPR_SR_DME.  With the data MMU disabled the
CPU performs no translation or protection on data accesses, so the task
gains read and write access to arbitrary physical memory, a local
privilege escalation.  SPR_SR_IME, SPR_SR_SUMRA, SPR_SR_LEE, SPR_SR_EPH
and the cache-enable bits are exposed the same way.  The ptrace GPR regset
already refuses any change to SR for exactly this reason.

Restore only the arithmetic flag bits (F, CY, OV) from the signal frame
and take every privileged control bit from the SR the kernel saved on
signal entry.

Verified with qemu-system-or1k -M or1k-sim: before this change an
unprivileged PoC clears SPR_SR_DME in rt_sigreturn and writes a marker to
physical address 0x03000000 (beyond the kernel's mem=32M); afterwards the
same PoC receives SIGSEGV and physical memory is unchanged.

## References
- https://git.kernel.org/stable/c/212fc482ddd7f9ccdd74a05eab1cac849350dcd6
- https://git.kernel.org/stable/c/32ef1b30ad736519f7a207bcc2986f3d4129d972
- https://git.kernel.org/stable/c/89a91b30685c0493b0fa2b47d0ab41061a63069d
- https://git.kernel.org/stable/c/a88d688be8d7f03cbf927f2ab454ea9fa58d2979
- https://git.kernel.org/stable/c/b4d73c3848bae9084fa8b9b2aa76d99a7d8eb17d
- https://git.kernel.org/stable/c/bc2e24ba6e167ccf374a197457aa5640a802f429
- https://git.kernel.org/stable/c/cd8b43a71755c516f5c1f265a103438ae9ab15be
- https://git.kernel.org/stable/c/cf1b5514ddf9df098ce7e3741fc9679fd85a4ec6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80560.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80560
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
