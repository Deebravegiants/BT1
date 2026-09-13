# [H] platform/x86: dell_rbu: Fix list usage

## Summary
Severity: High
Advisory: CVE-2025-38197
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38197
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

platform/x86: dell_rbu: Fix list usage

Pass the correct list head to list_for_each_entry*() when looping through
the packet list.

Without this patch, reading the packet data via sysfs will show the data
incorrectly (because it starts at the wrong packet), and clearing the
packet list will result in a NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/07d7b8e7ef7d1f812a6211ed531947c56d09e95e
- https://git.kernel.org/stable/c/32d05e6cc3a7bf6c8f16f7b7ef8fe80eca0c233e
- https://git.kernel.org/stable/c/4d71f2c1e5263a9f042faa71d59515709869dc79
- https://git.kernel.org/stable/c/5e8c658acd1b7c186aeffa46bf08795e121f401a
- https://git.kernel.org/stable/c/61ce04601e0d8265ec6d2ffa6df5a7e1bce64854
- https://git.kernel.org/stable/c/a7b477b64ef5e37cb08dd536ae07c46f9f28262e
- https://git.kernel.org/stable/c/f3b840fb1508a80cd8a0efb5c886ae1995a88b24
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38197.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38197
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
