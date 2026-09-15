# [C] net: tls: fix use-after-free with partial reads and async decrypt

## Summary
Severity: Critical
Advisory: CVE-2024-26582
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-26582
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tls: fix use-after-free with partial reads and async decrypt

tls_decrypt_sg doesn't take a reference on the pages from clear_skb,
so the put_page() in tls_decrypt_done releases them, and we trigger
a use-after-free in process_rx_list when we try to read from the
partially-read skb.

## References
- https://git.kernel.org/stable/c/20b4ed034872b4d024b26e2bc1092c3f80e5db96
- https://git.kernel.org/stable/c/32b55c5ff9103b8508c1e04bfa5a08c64e7a925f
- https://git.kernel.org/stable/c/754c9bab77a1b895b97bd99d754403c505bc79df
- https://git.kernel.org/stable/c/d684763534b969cca1022e2a28645c7cc91f7fa5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EZOU3745CWCDZ7EMKMXB2OEEIB5Q3IWM/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26582.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26582
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
