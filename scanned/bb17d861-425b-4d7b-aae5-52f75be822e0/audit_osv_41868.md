# [C] net: mana: validate rx_req_idx to prevent out-of-bounds array access

## Summary
Severity: Critical
Advisory: CVE-2026-64018
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64018
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: validate rx_req_idx to prevent out-of-bounds array access

In mana_hwc_rx_event_handler(), rx_req_idx is derived from
sge->address in DMA-coherent memory. In Confidential VMs
(SEV-SNP/TDX), this memory is shared unencrypted and HW can modify
WQE contents at any time. No bounds check exists on rx_req_idx,
which can lead to an out-of-bounds access into reqs[].

Add bounds check on rx_req_idx in mana_hwc_rx_event_handler() before
using it to index the reqs[] array.

## References
- https://git.kernel.org/stable/c/01f7f893d5e1baae995beeb86cd0f3e6bb2a3b01
- https://git.kernel.org/stable/c/355e9f2b2a7887ca38100127989af3e422ba71d0
- https://git.kernel.org/stable/c/5ddc715324badd7f2641bc177db1d027b402adae
- https://git.kernel.org/stable/c/763a372d344fb12fae566d36ddb46e92454ad58c
- https://git.kernel.org/stable/c/b809d0409991b75a6cff846a5ac27c3062953f84
- https://git.kernel.org/stable/c/fa627a5eaa83fc0261f44ef3769693b886ca6e27
- https://git.kernel.org/stable/c/ff1d5af207bcea857d45fe81505f1bc4b29eaef0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64018.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64018
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
