# [M] CVE-2021-47608

## Summary
Severity: Medium
Advisory: CVE-2021-47608
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47608
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix kernel address leakage in atomic fetch

The change in commit 37086bfdc737 ("bpf: Propagate stack bounds to registers
in atomics w/ BPF_FETCH") around check_mem_access() handling is buggy since
this would allow for unprivileged users to leak kernel pointers. For example,
an atomic fetch/and with -1 on a stack destination which holds a spilled
pointer will migrate the spilled register type into a scalar, which can then
be exported out of the program (since scalar != pointer) by dumping it into
a map value.

The original implementation of XADD was preventing this situation by using
a double call to check_mem_access() one with BPF_READ and a subsequent one
with BPF_WRITE, in both cases passing -1 as a placeholder value instead of
register as per XADD semantics since it didn't contain a value fetch. The
BPF_READ also included a check in check_stack_read_fixed_off() which rejects
the program if the stack slot is of __is_pointer_value() if dst_regno < 0.
The latter is to distinguish whether we're dealing with a regular stack spill/
fill or some arithmetical operation which is disallowed on non-scalars, see
also 6e7e63cbb023 ("bpf: Forbid XADD on spilled pointers for unprivileged
users") for more context on check_mem_access() and its handling of placeholder
value -1.

One minimally intrusive option to fix the leak is for the BPF_FETCH case to
initially check the BPF_READ case via check_mem_access() with -1 as register,
followed by the actual load case with non-negative load_reg to propagate
stack bounds to registers.

## References
- https://git.kernel.org/stable/c/423628125a484538111c2c6d9bb1588eb086053b
- https://git.kernel.org/stable/c/7d3baf0afa3aa9102d6a521a8e4c41888bb79882
