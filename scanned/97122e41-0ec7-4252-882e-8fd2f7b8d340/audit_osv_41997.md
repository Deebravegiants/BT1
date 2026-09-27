# [H] KVM: arm64: Clear __hyp_running_vcpu when flushing the pKVM hyp vCPU

## Summary
Severity: High
Advisory: CVE-2026-64286
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64286
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Clear __hyp_running_vcpu when flushing the pKVM hyp vCPU

flush_hyp_vcpu() copies the host vCPU context into the hyp's private
vCPU on every run. ctxt_to_vcpu() expects a guest context to have a
NULL __hyp_running_vcpu, which is only ever set on the host context, so
that it resolves the vCPU via container_of(). While this is generally
the case, flush_hyp_vcpu() copies the context verbatim and does not
enforce this, so a value provided by the host is dereferenced at EL2
(host -> EL2).

Fix by clearing __hyp_running_vcpu after the copy.

## References
- https://git.kernel.org/stable/c/477145860dba4c30f0b4e36f02f4c5291c1c888b
- https://git.kernel.org/stable/c/6bea2f8becdb20d34378493c3b77a9b9cf8c6cfa
- https://git.kernel.org/stable/c/d4f4d61715d1061ba83b88196a3605662be30750
- https://git.kernel.org/stable/c/dfaef40d8a1533940fc1af788d70fce07362b4ce
- https://git.kernel.org/stable/c/e8042f6e1d7befb2fb6b10a75918642bcd0acf9a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64286.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
