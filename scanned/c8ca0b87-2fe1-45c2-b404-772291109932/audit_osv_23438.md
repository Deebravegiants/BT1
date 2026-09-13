# [H] iwlwifi: fix use-after-free

## Summary
Severity: High
Advisory: CVE-2022-48787
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48787
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.263 <4.14.268, >=4.19.226 <4.19.231, >=5.4.174 <5.4.181, >=5.10.94 <5.10.102, >=5.15.17 <5.15.25, >=5.16.3 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

iwlwifi: fix use-after-free

If no firmware was present at all (or, presumably, all of the
firmware files failed to parse), we end up unbinding by calling
device_release_driver(), which calls remove(), which then in
iwlwifi calls iwl_drv_stop(), freeing the 'drv' struct. However
the new code I added will still erroneously access it after it
was freed.

Set 'failure=false' in this case to avoid the access, all data
was already freed anyway.

## References
- https://git.kernel.org/stable/c/008508c16af0087cda0394e1ac6f0493b01b6063
- https://git.kernel.org/stable/c/494de920d98f125b099f27a2d274850750aff957
- https://git.kernel.org/stable/c/7d6475179b85a83186ccce59cdc359d4f07d0bcb
- https://git.kernel.org/stable/c/9958b9cbb22145295ee1ffaea0904c383da2c05d
- https://git.kernel.org/stable/c/bea2662e7818e15d7607d17d57912ac984275d94
- https://git.kernel.org/stable/c/d3b98fe36f8a06ce654049540773256ab59cb53d
- https://git.kernel.org/stable/c/ddd46059f7d99119b62d44c519df7a79f2e6a515
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48787.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48787
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
