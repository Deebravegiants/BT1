# [M] CVE-2017-8106

## Summary
Severity: Medium
Advisory: CVE-2017-8106
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-24
Source: https://osv.dev/vulnerability/CVE-2017-8106
Type: osv

## Details
The handle_invept function in arch/x86/kvm/vmx.c in the Linux kernel 3.12 through 3.15 allows privileged KVM guest OS users to cause a denial of service (NULL pointer dereference and host OS crash) via a single-context INVEPT instruction with a NULL EPT pointer.

## References
- https://bugzilla.kernel.org/show_bug.cgi?id=195167
- https://launchpad.net/bugs/1678676
