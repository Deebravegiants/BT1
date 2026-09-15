# [H] net: sparx5: Fix use after free inside sparx5_del_mact_entry

## Summary
Severity: High
Advisory: CVE-2024-26856
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26856
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.152, >=5.16.0 <6.1.82, >=6.2.0 <6.6.22, >=6.7.0 <6.7.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sparx5: Fix use after free inside sparx5_del_mact_entry

Based on the static analyzis of the code it looks like when an entry
from the MAC table was removed, the entry was still used after being
freed. More precise the vid of the mac_entry was used after calling
devm_kfree on the mac_entry.
The fix consists in first using the vid of the mac_entry to delete the
entry from the HW and after that to free it.

## References
- https://git.kernel.org/stable/c/0de693d68b0a18d5e256556c7c62d92cca35ad52
- https://git.kernel.org/stable/c/71809805b95052ff551922f11660008fb3666025
- https://git.kernel.org/stable/c/89d72d4125e94aa3c2140fedd97ce07ba9e37674
- https://git.kernel.org/stable/c/e46274df1100fb0c06704195bfff5bfbd418bf64
- https://git.kernel.org/stable/c/e83bebb718fd1f42549358730e1206164e0861d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26856.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26856
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
