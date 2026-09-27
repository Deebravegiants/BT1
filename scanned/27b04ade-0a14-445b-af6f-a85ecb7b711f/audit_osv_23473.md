# [M] net: arcnet: com20020: Fix null-ptr-deref in com20020pci_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-48908
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2022-48908
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.305, >=4.10.0 <4.14.270, >=4.15.0 <4.19.233, >=4.20.0 <5.4.183, >=5.5.0 <5.10.104, >=5.11.0 <5.15.27, >=5.16.0 <5.16.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: arcnet: com20020: Fix null-ptr-deref in com20020pci_probe()

During driver initialization, the pointer of card info, i.e. the
variable 'ci' is required. However, the definition of
'com20020pci_id_table' reveals that this field is empty for some
devices, which will cause null pointer dereference when initializing
these devices.

The following log reveals it:

[    3.973806] KASAN: null-ptr-deref in range [0x0000000000000028-0x000000000000002f]
[    3.973819] RIP: 0010:com20020pci_probe+0x18d/0x13e0 [com20020_pci]
[    3.975181] Call Trace:
[    3.976208]  local_pci_probe+0x13f/0x210
[    3.977248]  pci_device_probe+0x34c/0x6d0
[    3.977255]  ? pci_uevent+0x470/0x470
[    3.978265]  really_probe+0x24c/0x8d0
[    3.978273]  __driver_probe_device+0x1b3/0x280
[    3.979288]  driver_probe_device+0x50/0x370

Fix this by checking whether the 'ci' is a null pointer first.

## References
- https://git.kernel.org/stable/c/5f394102ee27dbf051a4e283390cd8d1759dacea
- https://git.kernel.org/stable/c/8e3bc7c5bbf87e86e9cd652ca2a9166942d86206
- https://git.kernel.org/stable/c/b1ee6b9340a38bdb9e5c90f0eac5b22b122c3049
- https://git.kernel.org/stable/c/b838add93e1dd98210482dc433768daaf752bdef
- https://git.kernel.org/stable/c/bd6f1fd5d33dfe5d1b4f2502d3694a7cc13f166d
- https://git.kernel.org/stable/c/ca0bdff4249a644f2ca7a49d410d95b8dacf1f72
- https://git.kernel.org/stable/c/e50c589678e50f8d574612e473ca60ef45190896
- https://git.kernel.org/stable/c/ea372aab54903310756217d81610901a8e66cb7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48908.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48908
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
