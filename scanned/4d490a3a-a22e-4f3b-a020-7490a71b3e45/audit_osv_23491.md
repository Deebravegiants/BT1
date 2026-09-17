# [H] ravb: Fix potential use-after-free in ravb_rx_gbeth()

## Summary
Severity: High
Advisory: CVE-2022-48964
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-48964
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ravb: Fix potential use-after-free in ravb_rx_gbeth()

The skb is delivered to napi_gro_receive() which may free it, after calling this,
dereferencing skb may trigger use-after-free.

## References
- https://git.kernel.org/stable/c/5a5a3e564de6a8db987410c5c2f4748d50ea82b8
- https://git.kernel.org/stable/c/e63c681494dcc0527c625a0a4f59bf10259f5ee0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48964.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48964
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
