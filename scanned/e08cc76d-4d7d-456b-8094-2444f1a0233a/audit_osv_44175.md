# [H] s390/vfio_ccw: Implement a crw lock

## Summary
Severity: High
Advisory: CVE-2026-80547
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80547
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Implement a crw lock

Unlike the channel_program struct, which covers synchronous I/O
submissions and asynchronous interrupts, the CRW region relies
exclusively on asynchronous events coming from hardware.

Implement a lock to manage the list of those payloads, to ensure
they are read cohesively.

## References
- https://git.kernel.org/stable/c/0edd222730a9d7ec98368aaf1d40ee2d8d862e61
- https://git.kernel.org/stable/c/16b0798024c0e9117e395829ddbbe70981c79d9c
- https://git.kernel.org/stable/c/3c94d4179bcc19e01b28db634c07a58b28116209
- https://git.kernel.org/stable/c/49fa26b0df009dc1f420980bd71780e70615b83b
- https://git.kernel.org/stable/c/7902be374cbfc11c3435e1e87bf22195bf06a558
- https://git.kernel.org/stable/c/a3d60ae24183eee352c8e87a0ff94c97cd87f156
- https://git.kernel.org/stable/c/c76c4ee72bfc3824f4f491f18ed0323bf2e2daf9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80547.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80547
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
