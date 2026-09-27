# [M] bpf: Fix wrong reg type conversion in release_reference()

## Summary
Severity: Medium
Advisory: CVE-2022-49873
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49873
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix wrong reg type conversion in release_reference()

Some helper functions will allocate memory. To avoid memory leaks, the
verifier requires the eBPF program to release these memories by calling
the corresponding helper functions.

When a resource is released, all pointer registers corresponding to the
resource should be invalidated. The verifier use release_references() to
do this job, by apply  __mark_reg_unknown() to each relevant register.

It will give these registers the type of SCALAR_VALUE. A register that
will contain a pointer value at runtime, but of type SCALAR_VALUE, which
may allow the unprivileged user to get a kernel pointer by storing this
register into a map.

Using __mark_reg_not_init() while NOT allow_ptr_leaks can mitigate this
problem.

## References
- https://git.kernel.org/stable/c/466ce46f251dfb259a8cbaa895ab9edd6fb56240
- https://git.kernel.org/stable/c/ae5ccad6c711db0f2ca1231be051935dd128b8f5
- https://git.kernel.org/stable/c/cedd4f01f67be94735f15123158f485028571037
- https://git.kernel.org/stable/c/f1db20814af532f85e091231223e5e4818e8464b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49873.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49873
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
