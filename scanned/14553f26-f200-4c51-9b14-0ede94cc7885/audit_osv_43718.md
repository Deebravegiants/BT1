# [C] dibs: initialise dibs->lock in dibs_dev_alloc()

## Summary
Severity: Critical
Advisory: CVE-2026-74617
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74617
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

dibs: initialise dibs->lock in dibs_dev_alloc()

dibs->lock is initialised by dibs_dev_add(), but a dibs device can
already take interrupts before that call: ism_probe() runs
ism_dev_init(), and hence request_irq(), before it calls
dibs_dev_add(). No client can have registered a dmb at that point, so
no dmb interrupt can occur, but a GID event interrupt can, and
ism_handle_irq() takes dibs->lock unconditionally on entry, before it
inspects anything else.

Initialise the lock in dibs_dev_alloc() instead, so that it is valid as
soon as a driver can publish the device to its interrupt handler.

## References
- https://git.kernel.org/stable/c/2926031acba100d0c18fcfaa7a2ed29609318848
- https://git.kernel.org/stable/c/c27e360545373b7aee9862a5beef3b9fb3df0c25
- https://git.kernel.org/stable/c/fe79571f40434b257d68cbfb7b3ae93a794d8a11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74617.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74617
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
