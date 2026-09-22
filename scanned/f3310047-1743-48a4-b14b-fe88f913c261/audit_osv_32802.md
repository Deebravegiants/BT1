# [H] io_uring/fdinfo: grab ctx->uring_lock around io_uring_show_fdinfo()

## Summary
Severity: High
Advisory: CVE-2025-38002
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-06
Source: https://osv.dev/vulnerability/CVE-2025-38002
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.14.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/fdinfo: grab ctx->uring_lock around io_uring_show_fdinfo()

Not everything requires locking in there, which is why the 'has_lock'
variable exists. But enough does that it's a bit unwieldy to manage.
Wrap the whole thing in a ->uring_lock trylock, and just return
with no output if we fail to grab it. The existing trylock() will
already have greatly diminished utility/output for the failure case.

This fixes an issue with reading the SQE fields, if the ring is being
actively resized at the same time.

## References
- https://git.kernel.org/stable/c/bdb7d2ec2e31c46c45d1f32667dfa8216a72705e
- https://git.kernel.org/stable/c/d871198ee431d90f5308d53998c1ba1d5db5619a
- https://project-zero.issues.chromium.org/issues/417522668
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38002.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38002
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
