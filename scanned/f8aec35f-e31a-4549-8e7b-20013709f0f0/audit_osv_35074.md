# [H] bpf: account for current allocated stack depth in widen_imprecise_scalars()

## Summary
Severity: High
Advisory: CVE-2025-68208
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68208
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.117, >=6.7.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: account for current allocated stack depth in widen_imprecise_scalars()

The usage pattern for widen_imprecise_scalars() looks as follows:

    prev_st = find_prev_entry(env, ...);
    queued_st = push_stack(...);
    widen_imprecise_scalars(env, prev_st, queued_st);

Where prev_st is an ancestor of the queued_st in the explored states
tree. This ancestor is not guaranteed to have same allocated stack
depth as queued_st. E.g. in the following case:

    def main():
      for i in 1..2:
        foo(i)        // same callsite, differnt param

    def foo(i):
      if i == 1:
        use 128 bytes of stack
      iterator based loop

Here, for a second 'foo' call prev_st->allocated_stack is 128,
while queued_st->allocated_stack is much smaller.
widen_imprecise_scalars() needs to take this into account and avoid
accessing bpf_verifier_state->frame[*]->stack out of bounds.

## References
- https://git.kernel.org/stable/c/57e04e2ff56e32f923154f0f7bc476fcb596ffe7
- https://git.kernel.org/stable/c/64b12dca2b0abcb5fc0542887d18b926ea5cf711
- https://git.kernel.org/stable/c/9944c7938cd5b3f37b0afec0481c7c015e4f1c58
- https://git.kernel.org/stable/c/b0c8e6d3d866b6a7f73877f71968dbffd27b7785
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68208.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68208
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
