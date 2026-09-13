# [H] fsverity: Fix bpf_get_fsverity_digest() dynptr assumptions

## Summary
Severity: High
Advisory: CVE-2026-74590
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74590
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

fsverity: Fix bpf_get_fsverity_digest() dynptr assumptions

The BPF verifier and the dynptr abstraction ensure that the memory space
referenced by a dynptr remains valid.  They do not, however, provide any
guarantee that the contents of the memory are stable.  kfuncs are
expected to remain memory-safe even if concurrent modifications occur.

bpf_get_fsverity_digest() didn't follow that: it could crash if
arg->digest_size was concurrently modified.

Fix that by using the known-good value hash_alg->digest_size instead.

Also widen 'dynptr_sz' and 'out_digest_sz' to u64 to match the return
type of __bpf_dynptr_size().  It doesn't appear that it can actually be
more than INT_MAX currently (since __bpf_dynptr_data_rw() excludes
file-based pointers), but the correct type might as well be used.

## References
- https://git.kernel.org/stable/c/1344b632cb5043e32939a84568125719111c5af3
- https://git.kernel.org/stable/c/2a5cfcad1d56e26d645b7887b0ed24c371851525
- https://git.kernel.org/stable/c/3e8ec7c0387273329374f5c7bd61f5f38af71fe1
- https://git.kernel.org/stable/c/5bd63cad9df4328a184c409fbdad4f17944bcdb8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74590.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74590
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
