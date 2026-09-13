# [H] page_pool: always add GFP_NOWARN for ATOMIC allocations

## Summary
Severity: High
Advisory: CVE-2025-68321
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68321
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

page_pool: always add GFP_NOWARN for ATOMIC allocations

Driver authors often forget to add GFP_NOWARN for page allocation
from the datapath. This is annoying to users as OOMs are a fact
of life, and we pretty much expect network Rx to hit page allocation
failures during OOM. Make page pool add GFP_NOWARN for ATOMIC allocations
by default.

## References
- https://git.kernel.org/stable/c/0ec2cd5c58793d0c622797cd5fbe26634b357210
- https://git.kernel.org/stable/c/3671a0775952026228ae44e096eb144bca75f8dc
- https://git.kernel.org/stable/c/7613c06ffa89c1e2266fb532e23ef7dfdf269d73
- https://git.kernel.org/stable/c/9835a0fd59a1df5ec0740fdab6d50db68e0f10de
- https://git.kernel.org/stable/c/ab48dc0e23eb714b3f233f8e8f6deed7df2051f5
- https://git.kernel.org/stable/c/f3b52167a0cb23b27414452fbc1278da2ee884fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68321.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68321
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
