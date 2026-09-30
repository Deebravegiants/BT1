# [H] can: bcm: add locking for bcm_op runtime updates

## Summary
Severity: High
Advisory: CVE-2025-38004
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-06-08
Source: https://osv.dev/vulnerability/CVE-2025-38004
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: add locking for bcm_op runtime updates

The CAN broadcast manager (CAN BCM) can send a sequence of CAN frames via
hrtimer. The content and also the length of the sequence can be changed
resp reduced at runtime where the 'currframe' counter is then set to zero.

Although this appeared to be a safe operation the updates of 'currframe'
can be triggered from user space and hrtimer context in bcm_can_tx().
Anderson Nascimento created a proof of concept that triggered a KASAN
slab-out-of-bounds read access which can be prevented with a spin_lock_bh.

At the rework of bcm_can_tx() the 'count' variable has been moved into
the protected section as this variable can be modified from both contexts
too.

## References
- https://git.kernel.org/stable/c/2a437b86ac5a9893c902f30ef66815bf13587bf6
- https://git.kernel.org/stable/c/7595de7bc56e0e52b74e56c90f7e247bf626d628
- https://git.kernel.org/stable/c/76c84c3728178b2d38d5604e399dfe8b0752645e
- https://git.kernel.org/stable/c/8f1c022541bf5a923c8d6fa483112c15250f30a4
- https://git.kernel.org/stable/c/c2aba69d0c36a496ab4f2e81e9c2b271f2693fd7
- https://git.kernel.org/stable/c/c4e8a172501e677ebd8ea9d9161d97dc4df56fbd
- https://git.kernel.org/stable/c/cc55dd28c20a6611e30596019b3b2f636819a4c0
- https://git.kernel.org/stable/c/fbd8fdc2b218e979cfe422b139b8f74c12419d1f
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38004.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38004
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
