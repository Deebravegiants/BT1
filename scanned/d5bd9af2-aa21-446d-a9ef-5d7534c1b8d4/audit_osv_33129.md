# [M] staging: gpib: Fix cb7210 pcmcia Oops

## Summary
Severity: Medium
Advisory: CVE-2025-39755
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-39755
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: gpib: Fix cb7210 pcmcia Oops

The  pcmcia_driver struct was still only using the old .name
initialization in the drv field. This led to a NULL pointer
deref Oops in strcmp called from pcmcia_register_driver.

Initialize the pcmcia_driver struct name field.

## References
- https://git.kernel.org/stable/c/7ec50077d7f6647cb6ba3a2a20a6c26f51259c7d
- https://git.kernel.org/stable/c/c1baf6528bcfd6a86842093ff3f8ff8caf309c12
- https://git.kernel.org/stable/c/c82ae06f49e70d1c14ee9c76c392345856d050c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39755.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39755
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
