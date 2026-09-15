# [M] Libevent: Dangling Pointer in `evbuffer_add_buffer_reference`

## Summary
Severity: Medium
Advisory: CVE-2026-63381
Aliases: GHSA-c2pj-cg4r-88c8
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63381
Type: osv

## Details
Libevent is an event notification library. Prior to 2.1.13 and 2.2.2-alpha, libevent has a use-after-free in buffer.c when evbuffer_add_buffer_reference processes an output buffer whose out_total_len is zero. evbuffer_free_all_chains frees the initial empty chain without resetting outbuf->first, outbuf->last, or outbuf->last_with_datap, and APPEND_CHAIN_MULTICAST subsequently dereferences the dangling chain pointer. A caller that can drive this buffer state can cause memory corruption or a process crash. This issue is fixed in versions 2.1.13 and 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.1.13-stable
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63381.json
- https://github.com/libevent/libevent/security/advisories/GHSA-c2pj-cg4r-88c8
- https://nvd.nist.gov/vuln/detail/CVE-2026-63381
- https://github.com/libevent/libevent/commit/5cb95ba2f804f8aff46f88d58391c71e1251cd1c
- https://github.com/libevent/libevent/commit/9db091b04f569be3a700fa9860ef02f90b830af9
