# [H] cpufreq: pcc: fix use-after-free and double free in _OSC evaluation

## Summary
Severity: High
Advisory: CVE-2026-64372
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64372
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpufreq: pcc: fix use-after-free and double free in _OSC evaluation

pcc_cpufreq_do_osc() calls acpi_evaluate_object() twice for the
two-phase _OSC negotiation. Between the two calls it freed
output.pointer but left output.length unchanged. Since
acpi_evaluate_object() treats a non-zero length with a non-NULL
pointer as an existing buffer to write into, the second call wrote
into freed memory (use-after-free). The subsequent kfree(output.pointer)
at out_free then freed the same pointer a second time (double free).

Reset output.pointer to NULL and output.length to ACPI_ALLOCATE_BUFFER
after freeing the first result, so ACPICA allocates a fresh buffer for
each phase independently.

## References
- https://git.kernel.org/stable/c/0e3c739a2f6fc1de5b19a8839ab80696b9cb2a29
- https://git.kernel.org/stable/c/266d3dd8b757b48a576e90f018b51f7b7563cc32
- https://git.kernel.org/stable/c/5cdb25f144b101083d8bf3fd023ad87fbe6850d7
- https://git.kernel.org/stable/c/632666a63116d8061c62a988d1ca39dcd6d27c9b
- https://git.kernel.org/stable/c/6ba6f6783be2ffeb2cbcdc9321c4b9f708f796f7
- https://git.kernel.org/stable/c/8e454e9d0bc03446d610ee49abec9dfd424f6541
- https://git.kernel.org/stable/c/982c9f92d57bda2b769851ff6d90d43dcf5f3734
- https://git.kernel.org/stable/c/a36ca93a8ba57464e521d70a337d37f069064111
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64372.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64372
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
