# [H] net: hns3: add vlan list lock to protect vlan list

## Summary
Severity: High
Advisory: CVE-2022-49182
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49182
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: add vlan list lock to protect vlan list

When adding port base VLAN, vf VLAN need to remove from HW and modify
the vlan state in vf VLAN list as false. If the periodicity task is
freeing the same node, it may cause "use after free" error.
This patch adds a vlan list lock to protect the vlan list.

## References
- https://git.kernel.org/stable/c/09e383ca97e798f9954189b741af54b5c51e7a97
- https://git.kernel.org/stable/c/1932a624ab88ff407d1a1d567fe581faa15dc725
- https://git.kernel.org/stable/c/30f0ff7176efe8ac6c55f85bce26ed58bb608758
- https://git.kernel.org/stable/c/f58af41deeab0f45c9c80adf5f2de489ebbac3dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49182.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49182
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
