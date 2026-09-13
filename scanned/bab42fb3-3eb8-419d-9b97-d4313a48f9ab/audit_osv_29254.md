# [H] powerpc/eeh: avoid possible crash when edev->pdev changes

## Summary
Severity: High
Advisory: CVE-2024-41064
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41064
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/eeh: avoid possible crash when edev->pdev changes

If a PCI device is removed during eeh_pe_report_edev(), edev->pdev
will change and can cause a crash, hold the PCI rescan/remove lock
while taking a copy of edev->pdev->bus.

## References
- https://git.kernel.org/stable/c/033c51dfdbb6b79ab43fb3587276fa82d0a329e1
- https://git.kernel.org/stable/c/428d940a8b6b3350b282c14d3f63350bde65c48b
- https://git.kernel.org/stable/c/4bc246d2d60d071314842fa448faa4ed39082aff
- https://git.kernel.org/stable/c/4fad7fef847b6028475dd7b4c14fcb82b3e51274
- https://git.kernel.org/stable/c/8836e1bf5838ac6c08760e0a2dd7cf6410aa7ff3
- https://git.kernel.org/stable/c/a1216e62d039bf63a539bbe718536ec789a853dd
- https://git.kernel.org/stable/c/f23c3d1ca9c4b2d626242a4e7e1ec1770447f7b5
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41064.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41064
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
