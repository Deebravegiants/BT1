# [H] io_uring: fix io_req_prep_async with provided buffers

## Summary
Severity: High
Advisory: CVE-2025-40364
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-40364
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: fix io_req_prep_async with provided buffers

io_req_prep_async() can import provided buffers, commit the ring state
by giving up on that before, it'll be reimported later if needed.

## References
- https://git.kernel.org/stable/c/233b210a678bddf8b49b02a070074a52b87e6d43
- https://git.kernel.org/stable/c/35ae7910c349fb3c60439992e2e0e79061e95382
- https://git.kernel.org/stable/c/a1b17713b32c75a90132ea2f92b1257f3bbc20f3
- https://git.kernel.org/stable/c/a94592ec30ff67dc36c424327f1e0a9ceeeb9bd3
- https://git.kernel.org/stable/c/b86f1d51731e621e83305dc9564ae14c9ef752bf
- https://git.kernel.org/stable/c/d63b0e8a628e62ca85a0f7915230186bb92f8bb4
- https://git.kernel.org/stable/c/f0ef94553868d07c1b14d7743a7e2553e5a831a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40364.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
