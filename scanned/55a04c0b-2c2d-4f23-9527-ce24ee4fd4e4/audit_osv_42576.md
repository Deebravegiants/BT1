# [H] binder: cache secctx size before release zeroes it

## Summary
Severity: High
Advisory: CVE-2026-68458
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68458
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

binder: cache secctx size before release zeroes it

binder_transaction() bounds the scatter-gather buffer area with
sg_buf_end_offset and subtracts the aligned LSM context size because
the secctx is written at the tail of that area.  The subtraction reads
lsmctx.len, but that field has already been cleared by the time the
line runs:

    security_secid_to_secctx(secid, &lsmctx)   /* lsmctx.len set */
    lsmctx_aligned_size = ALIGN(lsmctx.len, sizeof(u64))
    extra_buffers_size += lsmctx_aligned_size
    ...
    security_release_secctx(&lsmctx)            /* memset zeroes len */
    ...
    sg_buf_end_offset = sg_buf_offset + extra_buffers_size
                        - ALIGN(lsmctx.len, sizeof(u64)) /* ALIGN(0,8) */

security_release_secctx() does memset(cp, 0, sizeof(*cp)), so lsmctx.len
reads back as 0 and the subtraction contributes nothing, leaving
sg_buf_end_offset too large by the aligned secctx size on every
transaction to a txn_security_ctx node.

Each BINDER_TYPE_PTR object then derives buf_left = sg_buf_end_offset -
sg_buf_offset as the sole upper bound on its copy, so the inflated end
offset lets the copy run into the bytes that already hold the secctx.

The aligned size must therefore be cached before release rather than
re-read from the now-cleared field.  Fix by caching it in
lsmctx_aligned_size at function scope when it is first computed and
subtracting lsmctx_aligned_size instead of re-reading lsmctx.len after
release.  Reuse the same value for the earlier buf_offset computation.

## References
- https://git.kernel.org/stable/c/1228926e1e4d605cc74d9e675558982a6f2cf446
- https://git.kernel.org/stable/c/4257f45ee1fddd0558e77b62af8bb63fd87b2162
- https://git.kernel.org/stable/c/b34826e55aad3520ec813f1f367c11b24b29dc9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68458.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68458
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
