# [H] CVE-2021-47255

## Summary
Severity: High
Advisory: CVE-2021-47255
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47255
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

kvm: LAPIC: Restore guard to prevent illegal APIC register access

Per the SDM, "any access that touches bytes 4 through 15 of an APIC
register may cause undefined behavior and must not be executed."
Worse, such an access in kvm_lapic_reg_read can result in a leak of
kernel stack contents. Prior to commit 01402cf81051 ("kvm: LAPIC:
write down valid APIC registers"), such an access was explicitly
disallowed. Restore the guard that was removed in that commit.

## References
- https://git.kernel.org/stable/c/218bf772bddd221489c38dde6ef8e917131161f6
- https://git.kernel.org/stable/c/a2aff09807fbe4018c269d3773a629949058b210
- https://git.kernel.org/stable/c/bf99ea52970caeb4583bdba1192c1f9b53b12c84
- https://git.kernel.org/stable/c/018685461a5b9a9a70e664ac77aef0d7415a3fd5
