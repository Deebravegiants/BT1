# [H] netfilter: nf_queue: fix possible use-after-free

## Summary
Severity: High
Advisory: CVE-2022-48911
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2022-48911
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <4.9.305, >=4.10.0 <4.14.270, >=4.15.0 <4.19.233, >=4.20.0 <5.4.183, >=5.5.0 <5.10.104, >=5.11.0 <5.15.27, >=5.16.0 <5.16.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_queue: fix possible use-after-free

Eric Dumazet says:
  The sock_hold() side seems suspect, because there is no guarantee
  that sk_refcnt is not already 0.

On failure, we cannot queue the packet and need to indicate an
error.  The packet will be dropped by the caller.

v2: split skb prefetch hunk into separate change

## References
- https://git.kernel.org/stable/c/21b27b2baa27423286e9b8d3f0b194d587083d95
- https://git.kernel.org/stable/c/34dc4a6a7f261736ef7183868a5bddad31c7f9e3
- https://git.kernel.org/stable/c/43c25da41e3091b31a906651a43e80a2719aa1ff
- https://git.kernel.org/stable/c/4d05239203fa38ea8a6f31e228460da4cb17a71a
- https://git.kernel.org/stable/c/c3873070247d9e3c7a6b0cf9bf9b45e8018427b1
- https://git.kernel.org/stable/c/dcc3cb920bf7ba66ac5e9272293a9ba5f80917ee
- https://git.kernel.org/stable/c/dd648bd1b33a828f62befa696b206c688da0ec43
- https://git.kernel.org/stable/c/ef97921ccdc243170fcef857ba2a17cf697aece5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48911.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48911
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
