# [H] CVE-2017-14316

## Summary
Severity: High
Advisory: CVE-2017-14316
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/CVE-2017-14316
Type: osv

## Details
A parameter verification issue was discovered in Xen through 4.9.x. The function `alloc_heap_pages` allows callers to specify the first NUMA node that should be used for allocations through the `memflags` parameter; the node is extracted using the `MEMF_get_node` macro. While the function checks to see if the special constant `NUMA_NO_NODE` is specified, it otherwise does not handle the case where `node >= MAX_NUMNODES`. This allows an out-of-bounds access to an internal array.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00009.html
- https://support.citrix.com/article/CTX227185
- http://www.securitytracker.com/id/1039348
- https://www.debian.org/security/2017/dsa-4050
- http://www.securityfocus.com/bid/100818
- http://xenbits.xen.org/xsa/advisory-231.html
