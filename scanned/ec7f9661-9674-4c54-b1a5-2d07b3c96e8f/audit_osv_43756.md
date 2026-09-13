# [H] s390/ism: Fix UAF of sba and ieq during ism_dev_exit()

## Summary
Severity: High
Advisory: CVE-2026-74690
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74690
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/ism: Fix UAF of sba and ieq during ism_dev_exit()

A ism interrupt handler can be active in parallel with ism_dev_exit(),
accessing freed data structures.

No new interrupts will be generated after unregister_ieq(). Drain ongoing
interrupt handlers by free_irq(), before freeing ism data structures.

## References
- https://git.kernel.org/stable/c/774394d27930ec4cf4cb3eed8ab6a4d20cb2430a
- https://git.kernel.org/stable/c/b1896543ce59c4258625a35cf41e23a9a1f80ea2
- https://git.kernel.org/stable/c/fc3021284050ecb3bba8a7851340cedcb5037928
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74690.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74690
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
