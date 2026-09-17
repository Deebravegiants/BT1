# [H] um: Add winch to winch_handlers before registering winch IRQ

## Summary
Severity: High
Advisory: CVE-2024-39292
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-24
Source: https://osv.dev/vulnerability/CVE-2024-39292
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

um: Add winch to winch_handlers before registering winch IRQ

Registering a winch IRQ is racy, an interrupt may occur before the winch is
added to the winch_handlers list.

If that happens, register_winch_irq() adds to that list a winch that is
scheduled to be (or has already been) freed, causing a panic later in
winch_cleanup().

Avoid the race by adding the winch to the winch_handlers list before
registering the IRQ, and rolling back if um_request_irq() fails.

## References
- https://git.kernel.org/stable/c/0c02d425a2fbe52643a5859a779db0329e7dddd4
- https://git.kernel.org/stable/c/31960d991e43c8d6dc07245f19fc13398e90ead2
- https://git.kernel.org/stable/c/351d1a64544944b44732f6a64ed65573b00b9e14
- https://git.kernel.org/stable/c/434a06c38ee1217a8baa0dd7c37cc85d50138fb0
- https://git.kernel.org/stable/c/66ea9a7c6824821476914bed21a476cd20094f33
- https://git.kernel.org/stable/c/73b8e21f76c7dda4905655d2e2c17dc5a73b87f1
- https://git.kernel.org/stable/c/a0fbbd36c156b9f7b2276871d499c9943dfe5101
- https://git.kernel.org/stable/c/dc1ff95602ee908fcd7d8acee7a0dadb61b1a0c0
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39292.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39292
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
