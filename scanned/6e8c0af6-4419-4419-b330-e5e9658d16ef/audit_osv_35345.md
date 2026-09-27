# [H] net: hns3: add VLAN id validation before using

## Summary
Severity: High
Advisory: CVE-2025-71112
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71112
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hns3: add VLAN id validation before using

Currently, the VLAN id may be used without validation when
receive a VLAN configuration mailbox from VF. The length of
vlan_del_fail_bmap is BITS_TO_LONGS(VLAN_N_VID). It may cause
out-of-bounds memory access once the VLAN id is bigger than
or equal to VLAN_N_VID.

Therefore, VLAN id needs to be checked to ensure it is within
the range of VLAN_N_VID.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/00e56a7706e10b3d00a258d81fcb85a7e96372d6
- https://git.kernel.org/stable/c/42c91dfa772c57de141e5a55a187ac760c0fd7e1
- https://git.kernel.org/stable/c/46c7d9fe8dd869ea5de666aba8c1ec1061ca44a8
- https://git.kernel.org/stable/c/6ef935e65902bfed53980ad2754b06a284ea8ac1
- https://git.kernel.org/stable/c/91a51d01be5c9f82c12c2921ca5cceaa31b67128
- https://git.kernel.org/stable/c/95cca255a7a5ad782639ff0298c2a486707d1046
- https://git.kernel.org/stable/c/b7b4f3bf118f51b67691a55b464f04452e5dc6fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71112.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
