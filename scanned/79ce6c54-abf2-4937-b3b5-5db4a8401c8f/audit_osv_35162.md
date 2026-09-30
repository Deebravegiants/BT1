# [H] drm/panthor: Fix UAF race between device unplug and FW event processing

## Summary
Severity: High
Advisory: CVE-2025-68748
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68748
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.63, >=6.13.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Fix UAF race between device unplug and FW event processing

The function panthor_fw_unplug() will free the FW memory sections.
The problem is that there could still be pending FW events which are yet
not handled at this point. process_fw_events_work() can in this case try
to access said freed memory.

Simply call disable_work_sync() to both drain and prevent future
invocation of process_fw_events_work().

## References
- https://git.kernel.org/stable/c/31db188355a49337e3e8ec98b99377e482eab22c
- https://git.kernel.org/stable/c/5e3ff56d4cb591daea70786d07dc21d06dc34108
- https://git.kernel.org/stable/c/6c1da9ae2c123a9ffda5375e64cc81f9ed3cc04a
- https://git.kernel.org/stable/c/7051f6ba968fa69918d72cc26de4d6cf7ea05b90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68748.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
