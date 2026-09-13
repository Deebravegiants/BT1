# [H] batman-adv: dat: handle forward allocation error

## Summary
Severity: High
Advisory: CVE-2026-52922
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52922
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: dat: handle forward allocation error

batadv_dat_forward_data() calls pskb_copy_for_clone() to duplicate an skb
for each DHT candidate, but does not check the return value before passing
it to batadv_send_skb_prepare_unicast_4addr(). That function dereferences
the skb unconditionally, so a failed allocation triggers a NULL pointer
dereference.

Skip forwarding to the current DHT candidate on allocation failure.

## References
- https://git.kernel.org/stable/c/2d8826a2d3657cea66fb0370f9e521575a673871
- https://git.kernel.org/stable/c/2edb8aeb3cdda9d00ec4997252dc5bcd6f54d8ef
- https://git.kernel.org/stable/c/4d420d9ee70a220a2cd95aa0dd2e15acad66a505
- https://git.kernel.org/stable/c/866ac1d57040ed0b44ca732e3c66b3aa6b93011c
- https://git.kernel.org/stable/c/9bcebaedfb8479cb4affb23c7a0d000ca9a20e73
- https://git.kernel.org/stable/c/9cceea8eeba710def2a5707ee00f00c74a9a1cac
- https://git.kernel.org/stable/c/ce0c381199402a2c58f4599f4f6ed100d872d0da
- https://git.kernel.org/stable/c/cf48e75fc4fe0d5cc7721c82d454221d01367b93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52922.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
