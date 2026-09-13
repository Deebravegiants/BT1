# [H] ACPI: NFIT: core: Fix acpi_nfit_init() error cleanup

## Summary
Severity: High
Advisory: CVE-2026-64510
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64510
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: NFIT: core: Fix acpi_nfit_init() error cleanup

If acpi_nfit_init() fails after adding the acpi_desc object to the
acpi_descs list, that object is never removed from that list because
the acpi_nfit_shutdown() devm action is not added for the NFIT device
in that case.  Next, the acpi_nfit_init() failure causes
acpi_nfit_probe() to fail, the acpi_desc object is freed, and a
dangling pointer is left behind in the acpi_descs.  Any subsequent
ACPI Machine Check Exception will trigger nfit_handle_mce() which
iterates over acpi_descs and so a use-after-free will occur.

Moreover, if acpi_nfit_probe() returns 0 after installing a notify
handler for the NFIT device and without allocating the acpi_desc
object and setting the NFIT device's driver data pointer, the
acpi_desc object will be allocated by acpi_nfit_update_notify()
and acpi_nfit_init() will be called to initialize it.  Regardless
of whether or not acpi_nfit_init() fails in that case, the
acpi_nfit_shutdown() devm action is not added for the NFIT device
and acpi_desc is never removed from the acpi_descs list.  If the
acpi_desc object is freed subsequently on driver removal, any
subsequent ACPI MCE will lead to a use-after-free like in the
previous case.

To address the first issue mentioned above, make acpi_nfit_probe()
call acpi_nfit_shutdown() directly on acpi_nfit_init() failures and
to address the other one, add a remove callback to the driver and
make it call acpi_nfit_shutdown().  Also, since it is now possible to
pass NULL to acpi_nfit_shutdown() or the acpi_desc object passed to it
may not have been initialized, add checks against NULL for acpi_desc and
its nvdimm_bus field to that function and make acpi_nfit_unregister()
clear the latter after unregistering the NVDIMM bus.

## References
- https://git.kernel.org/stable/c/38bf27511ef41bffebd157ec3eba41fc89ba59cd
- https://git.kernel.org/stable/c/3b2628f7682aea8d9ce09ad4b9a3bd144b451eaa
- https://git.kernel.org/stable/c/6ff054cc02a763914773b026cacb429e5fbf64fa
- https://git.kernel.org/stable/c/7d69235bdc581a4346e9bcd6a8bea37d3e1abd25
- https://git.kernel.org/stable/c/b07d22a2d17ad6465c87bd5752bc70e4c16e0ee4
- https://git.kernel.org/stable/c/c127dbd832bd4b9aef8a749d9f491b74042f9b47
- https://git.kernel.org/stable/c/df7c92216a1583a76cb0cbf2f21cd68870609b05
- https://git.kernel.org/stable/c/ee82078e776ae31266cc70fdf62ac17c3c6f100a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64510.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64510
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
