# [H] xsk: Harden userspace-supplied xdp_desc validation

## Summary
Severity: High
Advisory: CVE-2025-40159
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40159
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: Harden userspace-supplied xdp_desc validation

Turned out certain clearly invalid values passed in xdp_desc from
userspace can pass xp_{,un}aligned_validate_desc() and then lead
to UBs or just invalid frames to be queued for xmit.

desc->len close to ``U32_MAX`` with a non-zero pool->tx_metadata_len
can cause positive integer overflow and wraparound, the same way low
enough desc->addr with a non-zero pool->tx_metadata_len can cause
negative integer overflow. Both scenarios can then pass the
validation successfully.
This doesn't happen with valid XSk applications, but can be used
to perform attacks.

Always promote desc->len to ``u64`` first to exclude positive
overflows of it. Use explicit check_{add,sub}_overflow() when
validating desc->addr (which is ``u64`` already).

bloat-o-meter reports a little growth of the code size:

add/remove: 0/0 grow/shrink: 2/1 up/down: 60/-16 (44)
Function                                     old     new   delta
xskq_cons_peek_desc                          299     330     +31
xsk_tx_peek_release_desc_batch               973    1002     +29
xsk_generic_xmit                            3148    3132     -16

but hopefully this doesn't hurt the performance much.

## References
- https://git.kernel.org/stable/c/07ca98f906a403637fc5e513a872a50ef1247f3b
- https://git.kernel.org/stable/c/1463cd066f32efd56ddfd3ac4e3524200f362980
- https://git.kernel.org/stable/c/5b5fffa7c81e55d8c8edf05ad40d811ec7047e21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40159.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40159
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
