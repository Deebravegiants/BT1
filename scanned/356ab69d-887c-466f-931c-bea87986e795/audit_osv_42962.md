# [H] batman-adv: tt: avoid request storms during pending request

## Summary
Severity: High
Advisory: CVE-2026-72231
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72231
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: tt: avoid request storms during pending request

batadv_send_tt_request() allocates a tt_req_node when none exists for the
destination originator node. This should prevent that a multiple TT
requests are send at the same time to an originator.

But if allocation of the send buffer failed, this request must be cleaned
up again. But indicator for such a failure is "ret == false". But the
actual implementation is checking for "ret == true".

The check must be inverted to not loose the information about the TT
request directly after it was attempted to be sent out. This should avoid
potential request storms.

## References
- https://git.kernel.org/stable/c/067e413eec2e63c2996909ef55214b3a0eda0be7
- https://git.kernel.org/stable/c/21c44a6895f41df811d1c91d10eea194dda2b345
- https://git.kernel.org/stable/c/27c7d40008231ae4140d35501b60087a9de2d2c3
- https://git.kernel.org/stable/c/5e46c76d9a5062212c4c5f642a5549fd9c057f8a
- https://git.kernel.org/stable/c/6055695ea40c64a47e00742c12c99b1a33b4daed
- https://git.kernel.org/stable/c/6a65ac8a81e903bb4b555c1d13532f5cb0167a4a
- https://git.kernel.org/stable/c/716f434eb35869e130424331584a91fbb729b9bd
- https://git.kernel.org/stable/c/aba1cf21954e64c36afb966b754adad2b0b8aa48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72231.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72231
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
