# [H] gpib: fix double decrement of descriptor_busy in command_ioctl()

## Summary
Severity: High
Advisory: CVE-2026-72482
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72482
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpib: fix double decrement of descriptor_busy in command_ioctl()

commit d1857f8296dc ("gpib: fix use-after-free in IO ioctl handlers")
introduced a descriptor_busy reference counter to pin struct
gpib_descriptor across IO ioctl operations.  In command_ioctl(), the
error path inside the loop decrements descriptor_busy and breaks, but
execution then falls through to the unconditional decrement after the
loop, underflowing the counter to -1.

This re-enables the use-after-free that the original fix was meant to
prevent: a concurrent close_dev_ioctl() sees descriptor_busy == 0 on
an actively-used descriptor and frees it.

Remove the early decrement from the error path.  The post-loop
decrement already handles all exit paths, matching the correct pattern
used in read_ioctl() and write_ioctl().

## References
- https://git.kernel.org/stable/c/8b5f1d295dda8677e4545ce340053fcfa8b634c7
- https://git.kernel.org/stable/c/c4faab452b3c1ada003d49c477609dd80523b9bf
- https://git.kernel.org/stable/c/fdee9f207a48ce204ec6cfceaa1459d2473600a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72482.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72482
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
