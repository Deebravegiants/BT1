# [H] io_uring/af_unix: defer registered files gc to io_uring release

## Summary
Severity: High
Advisory: CVE-2022-50234
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50234
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/af_unix: defer registered files gc to io_uring release

Instead of putting io_uring's registered files in unix_gc() we want it
to be done by io_uring itself. The trick here is to consider io_uring
registered files for cycle detection but not actually putting them down.
Because io_uring can't register other ring instances, this will remove
all refs to the ring file triggering the ->release path and clean up
with io_ring_ctx_free().

[axboe: add kerneldoc comment to skb, fold in skb leak fix]

## References
- https://git.kernel.org/stable/c/0091bfc81741b8d3aeb3b7ab8636f911b2de6e80
- https://git.kernel.org/stable/c/04df9719df1865f6770af9bc7880874af0e594b2
- https://git.kernel.org/stable/c/75e94c7e8859e58aadc15a98cc9704edff47d4f2
- https://git.kernel.org/stable/c/813d8fe5d30388f73a21d3a2bf46b0a1fd72498c
- https://git.kernel.org/stable/c/b4293c01ee0d0ecdd3cb5801e13f62271144667a
- https://git.kernel.org/stable/c/c378c479c5175833bb22ff71974cda47d7b05401
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50234.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
