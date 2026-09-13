# [M] firmware: dmi-sysfs: Fix memory leak in dmi_sysfs_register_handle

## Summary
Severity: Medium
Advisory: CVE-2022-49370
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49370
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: dmi-sysfs: Fix memory leak in dmi_sysfs_register_handle

kobject_init_and_add() takes reference even when it fails.
According to the doc of kobject_init_and_add()

   If this function returns an error, kobject_put() must be called to
   properly clean up the memory associated with the object.

Fix this issue by calling kobject_put().

## References
- https://git.kernel.org/stable/c/3ba359ebe914ac3f8c6c832b28007c14c39d3766
- https://git.kernel.org/stable/c/660ba678f9998aca6db74f2dd912fa5124f0fa31
- https://git.kernel.org/stable/c/985706bd3bbeffc8737bc05965ca8d24837bc7db
- https://git.kernel.org/stable/c/a724634b2a49f6ff0177a9e19a5a92fc1545e1b7
- https://git.kernel.org/stable/c/a9bfb37d6ba7c376b0d53337a4c5f5ff324bd725
- https://git.kernel.org/stable/c/c66cc3c62870a27ea8f060a7e4c1ad8d26dd3f0d
- https://git.kernel.org/stable/c/ec752973aa721ee281d5441e497364637c626c7b
- https://git.kernel.org/stable/c/ed38d04342dfbe9e5aca745c8b5eb4188a74f0ef
- https://git.kernel.org/stable/c/fdffa4ad8f6bf1ece877edfb807f2b2c729d8578
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49370.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49370
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
