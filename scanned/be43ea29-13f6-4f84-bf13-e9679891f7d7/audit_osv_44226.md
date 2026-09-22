# [C] net: airoha: fix foe_check_time allocation size

## Summary
Severity: Critical
Advisory: CVE-2026-80617
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80617
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: airoha: fix foe_check_time allocation size

foe_check_time is declared as u16 pointer but was allocated with
only ppe_num_entries bytes instead of ppe_num_entries * sizeof(u16).

When airoha_ppe_foe_verify_entry() is called with hash >= ppe_num_entries/2,
it writes beyond the allocated buffer, causing heap buffer overflow and
potential kernel crash.

## References
- https://git.kernel.org/stable/c/112b5eff24e044561ee9599a0d34e0fcea1df4e0
- https://git.kernel.org/stable/c/5c121ee635680c93d7074becf14cfbaac140f80d
- https://git.kernel.org/stable/c/9f7cd1e26d2f1766438edc9b9254f2c618f9ae98
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80617.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80617
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
