# [H] bnxt: prevent skb UAF after handing over to PTP worker

## Summary
Severity: High
Advisory: CVE-2022-48637
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48637
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt: prevent skb UAF after handing over to PTP worker

When reading the timestamp is required bnxt_tx_int() hands
over the ownership of the completed skb to the PTP worker.
The skb should not be used afterwards, as the worker may
run before the rest of our code and free the skb, leading
to a use-after-free.

Since dev_kfree_skb_any() accepts NULL make the loss of
ownership more obvious and set skb to NULL.

## References
- https://git.kernel.org/stable/c/08483e4c0c83b221b8891434a04cec405dee94a6
- https://git.kernel.org/stable/c/32afa1f23e42cc635ccf4c39f24514d03d1e8338
- https://git.kernel.org/stable/c/c31f26c8f69f776759cbbdfb38e40ea91aa0dd65
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48637.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48637
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
