# [H] media: imx-jpeg: fix a bug of accessing array out of bounds

## Summary
Severity: High
Advisory: CVE-2022-49163
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49163
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: imx-jpeg: fix a bug of accessing array out of bounds

When error occurs in parsing jpeg, the slot isn't acquired yet, it may
be the default value MXC_MAX_SLOTS.
If the driver access the slot using the incorrect slot number, it will
access array out of bounds.
The result is the driver will change num_domains, which follows
slot_data in struct mxc_jpeg_dev.
Then the driver won't detach the pm domain at rmmod, which will lead to
kernel panic when trying to insmod again.

## References
- https://git.kernel.org/stable/c/02f9f97d54ffc85b50ad77f5b1f3c8f69cd17747
- https://git.kernel.org/stable/c/20c8b90430c5d6c4a3936eaa7c35aac670581487
- https://git.kernel.org/stable/c/97558d170a1236280407e8d29a7d095d2c2ed554
- https://git.kernel.org/stable/c/e209e6db2e527db6a93b14c2deedf969caca78fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49163.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49163
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
