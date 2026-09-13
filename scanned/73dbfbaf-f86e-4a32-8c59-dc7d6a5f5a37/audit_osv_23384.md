# [H] netfilter: nfnetlink_osf: fix possible bogus match in nf_osf_find()

## Summary
Severity: High
Advisory: CVE-2022-48654
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48654
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.215, >=5.5.0 <5.10.146, >=5.11.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink_osf: fix possible bogus match in nf_osf_find()

nf_osf_find() incorrectly returns true on mismatch, this leads to
copying uninitialized memory area in nft_osf which can be used to leak
stale kernel stack data to userspace.

## References
- https://git.kernel.org/stable/c/559c36c5a8d730c49ef805a72b213d3bba155cc8
- https://git.kernel.org/stable/c/5d75fef3e61e797fab5c3fbba88caa74ab92ad47
- https://git.kernel.org/stable/c/633c81c0449663f57d4138326d036dc6cfad674e
- https://git.kernel.org/stable/c/721ea8ac063d70c2078c4e762212705de6151764
- https://git.kernel.org/stable/c/816eab147e5c6f6621922b8515ad9010ceb1735e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48654.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48654
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
