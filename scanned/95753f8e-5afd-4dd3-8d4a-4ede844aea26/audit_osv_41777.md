# [C] net: airoha: Do not read uninitialized fragment address in airoha_dev_xmit()

## Summary
Severity: Critical
Advisory: CVE-2026-63857
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63857
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: airoha: Do not read uninitialized fragment address in airoha_dev_xmit()

The transmit loop in airoha_dev_xmit() reads fragment address and length
during its final iteration, when the loop index equals
skb_shinfo(skb)->nr_frags, at which point the fragment data is
uninitialized. While these values are never consumed, the read itself is
unsafe and may trigger a page fault. Fix this by avoiding the fragment
read on the last iteration.
Additionally, move the skb pointer from the first to the last used packet
descriptor, so that airoha_qdma_tx_napi_poll() defers freeing the skb
until the final descriptor is processed.

## References
- https://git.kernel.org/stable/c/bde34e84edc8b5571fbde7e941e175a4293ee1eb
- https://git.kernel.org/stable/c/d78c8ab7bd84952e053d0c622b7fc1b4ad8a19a3
- https://git.kernel.org/stable/c/f670fa4b19ceddc6d215dda4997888ccba9bbc61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63857.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63857
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
