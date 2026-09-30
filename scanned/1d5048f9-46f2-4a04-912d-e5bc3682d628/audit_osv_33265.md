# [H] i40e: fix idx validation in config queues msg

## Summary
Severity: High
Advisory: CVE-2025-39971
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39971
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.4.300, >=5.5.0 <5.10.245, >=5.11.0 <5.15.194, >=5.16.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: fix idx validation in config queues msg

Ensure idx is within range of active/initialized TCs when iterating over
vf->ch[idx] in i40e_vc_config_queues_msg().

## References
- https://git.kernel.org/stable/c/1fa0aadade34481c567cdf4a897c0d4e4d548bd1
- https://git.kernel.org/stable/c/2cc26dac0518d2fa9b67ec813ee60e183480f98a
- https://git.kernel.org/stable/c/5c1f96123113e0bdc6d8dc2b0830184c93da9f65
- https://git.kernel.org/stable/c/8b9c7719b0987b1c6c5fc910599f3618a558dbde
- https://git.kernel.org/stable/c/a6ff2af78343eceb0f77ab1a2fe802183bc21648
- https://git.kernel.org/stable/c/bfcc1dff429d4b99ba03e40ddacc68ea4be2b32b
- https://git.kernel.org/stable/c/f1ad24c5abe1eaef69158bac1405a74b3c365115
- https://git.kernel.org/stable/c/f5f91d164af22e7147130ef8bebbdb28d8ecc6e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39971.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39971
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
