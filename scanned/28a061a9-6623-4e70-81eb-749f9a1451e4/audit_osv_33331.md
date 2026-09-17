# [H] scsi: pm80xx: Fix array-index-out-of-of-bounds on rmmod

## Summary
Severity: High
Advisory: CVE-2025-40118
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40118
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: pm80xx: Fix array-index-out-of-of-bounds on rmmod

Since commit f7b705c238d1 ("scsi: pm80xx: Set phy_attached to zero when
device is gone") UBSAN reports:

  UBSAN: array-index-out-of-bounds in drivers/scsi/pm8001/pm8001_sas.c:786:17
  index 28 is out of range for type 'pm8001_phy [16]'

on rmmod when using an expander.

For a direct attached device, attached_phy contains the local phy id.
For a device behind an expander, attached_phy contains the remote phy
id, not the local phy id.

I.e. while pm8001_ha will have pm8001_ha->chip->n_phy local phys, for a
device behind an expander, attached_phy can be much larger than
pm8001_ha->chip->n_phy (depending on the amount of phys of the
expander).

E.g. on my system pm8001_ha has 8 phys with phy ids 0-7.  One of the
ports has an expander connected.  The expander has 31 phys with phy ids
0-30.

The pm8001_ha->phy array only contains the phys of the HBA.  It does not
contain the phys of the expander.  Thus, it is wrong to use attached_phy
to index the pm8001_ha->phy array for a device behind an expander.

Thus, we can only clear phy_attached for devices that are directly
attached.

## References
- https://git.kernel.org/stable/c/251be2f6037fb7ab399f68cd7428ff274133d693
- https://git.kernel.org/stable/c/45acbf154befedd9bc135f5e031fe7855d1e6493
- https://git.kernel.org/stable/c/83ced3c206c292458e47c7fac54223abc7141585
- https://git.kernel.org/stable/c/9326a1541e1b7ed3efdbab72061b82cf01c6477a
- https://git.kernel.org/stable/c/9c671d4dbfbfb0d73cfdfb706afb36d9ad60a582
- https://git.kernel.org/stable/c/d94be0a6ae9ade706d4270e740bdb4f79953a7fc
- https://git.kernel.org/stable/c/e62251954a128a2d0fcbc19e5fa39e08935bb628
- https://git.kernel.org/stable/c/eef5ef400893f8e3dbb09342583be0cdc716d566
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40118.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40118
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
