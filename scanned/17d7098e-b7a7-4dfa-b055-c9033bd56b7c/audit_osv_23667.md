# [M] tty: Fix a possible resource leak in icom_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49314
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49314
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: Fix a possible resource leak in icom_probe

When pci_read_config_dword failed, call pci_release_regions() and
pci_disable_device() to recycle the resource previously allocated.

## References
- https://git.kernel.org/stable/c/23e155b51d403c0ccedc60c0d6c3c452afed07fe
- https://git.kernel.org/stable/c/5f9b2e4ca88cab1a96b86ecd45544e488ca43faf
- https://git.kernel.org/stable/c/8c014373f178a4f13a08e045ef63bdb23f62e892
- https://git.kernel.org/stable/c/9a8305f357a8d03698fc7bc855ff9c6865d5486b
- https://git.kernel.org/stable/c/a2df0b4d080cc770b4da7bff487048c803dfd07e
- https://git.kernel.org/stable/c/cb7147afd328c07edeeee287710d8d96ac0459f5
- https://git.kernel.org/stable/c/d703d912a985c1c5b50dd38c3181fc3540fa77cb
- https://git.kernel.org/stable/c/ee157a79e7c82b01ae4c25de0ac75899801f322c
- https://git.kernel.org/stable/c/f4c836d90da1ece88905d62ce2ce39a962f25d1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49314.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
