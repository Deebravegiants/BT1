# [H] bpf: Fix linked reg delta tracking when src_reg == dst_reg

## Summary
Severity: High
Advisory: CVE-2026-53092
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53092
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.105, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix linked reg delta tracking when src_reg == dst_reg

Consider the case of rX += rX where src_reg and dst_reg are pointers to
the same bpf_reg_state in adjust_reg_min_max_vals(). The latter first
modifies the dst_reg in-place, and later in the delta tracking, the
subsequent is_reg_const(src_reg)/reg_const_value(src_reg) reads the
post-{add,sub} value instead of the original source.

This is problematic since it sets an incorrect delta, which sync_linked_regs()
then propagates to linked registers, thus creating a verifier-vs-runtime
mismatch. Fix it by just skipping this corner case.

## References
- https://git.kernel.org/stable/c/1509c1ae9185ec7103899967ed788b6eebab3fcc
- https://git.kernel.org/stable/c/cc86a8b0a1c54d2bccf6f68cf49b82dea91b84de
- https://git.kernel.org/stable/c/d7f14173c0d5866c3cae759dee560ad1bed10d2e
- https://git.kernel.org/stable/c/d88e8e4a3b52bd5b2ff3eceba4b29d1b5506d066
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53092.json
- https://access.redhat.com/security/cve/CVE-2026-53092
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53092.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53092
- https://bugzilla.redhat.com/show_bug.cgi?id=2492362
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
