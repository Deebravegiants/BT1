# [H] PCI: Check ROM header and data structure addr before accessing

## Summary
Severity: High
Advisory: CVE-2026-72487
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72487
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

PCI: Check ROM header and data structure addr before accessing

We meet a crash when running stress-ng on x86_64 machine:

  BUG: unable to handle page fault for address: ffa0000007f40000
  RIP: 0010:pci_get_rom_size+0x52/0x220
  Call Trace:
  <TASK>
    pci_map_rom+0x80/0x130
    pci_read_rom+0x4b/0xe0
    kernfs_file_read_iter+0x96/0x180
    vfs_read+0x1b1/0x300

Our analysis reveals that the ROM space's start address is
0xffa0000007f30000, and size is 0x10000. Because of broken ROM space,
before calling readl(pds), the pds's value is 0xffa0000007f3ffff, which is
already pointed to the ROM space end, invoking readl() would read 4 bytes
therefore cause an out-of-bounds access and trigger a crash.  Fix this by
adding image header and data structure checking.

We also found another crash on arm64 machine:

  Unable to handle kernel paging request at virtual address ffff8000dd1393ff
  Mem abort info:
  ESR = 0x0000000096000021
  EC = 0x25: DABT (current EL), IL = 32 bits
  SET = 0, FnV = 0
  EA = 0, S1PTW = 0
  FSC = 0x21: alignment fault

The call trace is the same with x86_64, but the crash reason is that the
data structure addr is not aligned with 4, and arm64 machine report
"alignment fault". Fix this by adding alignment checking.

[bhelgaas: shorten function names, wrap comments]

## References
- https://git.kernel.org/stable/c/1d495446ec7ace5b61da366ffb161ee8319dd9a2
- https://git.kernel.org/stable/c/4997873e3abbad47a9e1e4abd05f045f77a74f22
- https://git.kernel.org/stable/c/538796b807fcfb81b2ce40cc97a614fd8588feb5
- https://git.kernel.org/stable/c/721ad5b72448b5065ed309017ab563205f162404
- https://git.kernel.org/stable/c/724042f8f98d2594b9d164549fd4292c6bd58120
- https://git.kernel.org/stable/c/cd5b242d5848369b9e957340a7e30adee7b6763d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72487.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72487
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
