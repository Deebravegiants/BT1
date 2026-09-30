# [C] seg6: separate dst_cache for input and output paths in seg6 lwtunnel

## Summary
Severity: Critical
Advisory: CVE-2026-31668
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31668
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

seg6: separate dst_cache for input and output paths in seg6 lwtunnel

The seg6 lwtunnel uses a single dst_cache per encap route, shared
between seg6_input_core() and seg6_output_core(). These two paths
can perform the post-encap SID lookup in different routing contexts
(e.g., ip rules matching on the ingress interface, or VRF table
separation). Whichever path runs first populates the cache, and the
other reuses it blindly, bypassing its own lookup.

Fix this by splitting the cache into cache_input and cache_output,
so each path maintains its own cached dst independently.

## References
- https://git.kernel.org/stable/c/17d87d42874f5d6c1a0ccc6d9190dfe82a9a7a6a
- https://git.kernel.org/stable/c/1dec91d3b1cefb82635761b7812154af3ef46449
- https://git.kernel.org/stable/c/57d0374d14fa667dec6952173b93e7e84486d5c9
- https://git.kernel.org/stable/c/6305ad032b03d2ea4181b953a66e19a9a6ed053c
- https://git.kernel.org/stable/c/750569d6987a0ff46317a4b86eb3907e296287bf
- https://git.kernel.org/stable/c/84d458018b147176b259347103fccb7e93abd2b1
- https://git.kernel.org/stable/c/c3812651b522fe8437ebb7063b75ddb95b571643
- https://git.kernel.org/stable/c/fb56de5d99218de49d5d43ef3a99e062ecd0f9a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31668.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31668
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
