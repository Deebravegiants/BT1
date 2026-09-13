# [H] bpf: Fix out-of-bounds write in trie_get_next_key()

## Summary
Severity: High
Advisory: CVE-2024-50262
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50262
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix out-of-bounds write in trie_get_next_key()

trie_get_next_key() allocates a node stack with size trie->max_prefixlen,
while it writes (trie->max_prefixlen + 1) nodes to the stack when it has
full paths from the root to leaves. For example, consider a trie with
max_prefixlen is 8, and the nodes with key 0x00/0, 0x00/1, 0x00/2, ...
0x00/8 inserted. Subsequent calls to trie_get_next_key with _key with
.prefixlen = 8 make 9 nodes be written on the node stack with size 8.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/13400ac8fb80c57c2bfb12ebd35ee121ce9b4d21
- https://git.kernel.org/stable/c/590976f921723d53ac199c01d5b7b73a94875e68
- https://git.kernel.org/stable/c/86c8ebe02d8806dd8878d0063e8e185622ab6ea6
- https://git.kernel.org/stable/c/90a6e0e1e151ef7a9282e78f54c3091de2dcc99c
- https://git.kernel.org/stable/c/91afbc0eb3c90258ae378ae3c6ead3d2371e926d
- https://git.kernel.org/stable/c/a035df0b98df424559fd383e8e1a268f422ea2ba
- https://git.kernel.org/stable/c/c4b4f9a9ab82238cb158fa4fe61a8c0ae21a4980
- https://git.kernel.org/stable/c/e8494ac079814a53fbc2258d2743e720907488ed
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50262.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50262
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
