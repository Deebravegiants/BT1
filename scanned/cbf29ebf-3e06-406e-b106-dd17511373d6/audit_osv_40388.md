# [C] net: bcmgenet: fix racing timeout handler

## Summary
Severity: Critical
Advisory: CVE-2026-53086
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53086
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bcmgenet: fix racing timeout handler

The bcmgenet_timeout handler tries to take down all tx queues when
a single queue times out. This is over zealous and causes many race
conditions with queues that are still chugging along. Instead lets
only restart the timed out queue.

## References
- https://git.kernel.org/stable/c/5393b2b5bee2ac51a0043dc7f4ac3475f053d08d
- https://git.kernel.org/stable/c/681fdfe823b4f1036ed50b58b8838c7917ea389c
- https://git.kernel.org/stable/c/7ce1c26aac3b318886a57425f64b522da7389153
- https://git.kernel.org/stable/c/c270e2bec3e55a716d25c35341091339457ac883
- https://git.kernel.org/stable/c/e8206538cbaf4f4068e99a4cb1138690a1e00499
- https://git.kernel.org/stable/c/e85b0c0a12e967930044608311471b665baa315c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53086.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53086
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
