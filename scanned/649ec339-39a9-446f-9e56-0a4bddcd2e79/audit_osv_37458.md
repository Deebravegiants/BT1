# [H] rxrpc: Fix RxGK token loading to check bounds

## Summary
Severity: High
Advisory: CVE-2026-31641
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31641
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix RxGK token loading to check bounds

rxrpc_preparse_xdr_yfs_rxgk() reads the raw key length and ticket length
from the XDR token as u32 values and passes each through round_up(x, 4)
before using the rounded value for validation and allocation.  When the raw
length is >= 0xfffffffd, round_up() wraps to 0, so the bounds check and
kzalloc both use 0 while the subsequent memcpy still copies the original
~4 GiB value, producing a heap buffer overflow reachable from an
unprivileged add_key() call.

Fix this by:

 (1) Rejecting raw key lengths above AFSTOKEN_GK_KEY_MAX and raw ticket
     lengths above AFSTOKEN_GK_TOKEN_MAX before rounding, consistent with
     the caps that the RxKAD path already enforces via AFSTOKEN_RK_TIX_MAX.

 (2) Sizing the flexible-array allocation from the validated raw key
     length via struct_size_t() instead of the rounded value.

 (3) Caching the raw lengths so that the later field assignments and
     memcpy calls do not re-read from the token, eliminating a class of
     TOCTOU re-parse.

The control path (valid token with lengths within bounds) is unaffected.

## References
- https://git.kernel.org/stable/c/3e04596cba8a86cbff9c3f4bf0a524a3a488773c
- https://git.kernel.org/stable/c/49875b360c2b83a3c226e189c502e501d83e6445
- https://git.kernel.org/stable/c/d179a868dd755b0cfcf7582e00943d702b9943b8
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31641.json
- https://access.redhat.com/errata/RHSA-2026:27288
- https://access.redhat.com/errata/RHSA-2026:55618
- https://access.redhat.com/security/cve/CVE-2026-31641
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31641.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31641
- https://bugzilla.redhat.com/show_bug.cgi?id=2461548
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
