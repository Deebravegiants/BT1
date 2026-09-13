# [H] CVE-2021-3656

## Summary
Severity: High
Advisory: CVE-2021-3656
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-03-04
Source: https://osv.dev/vulnerability/CVE-2021-3656
Type: osv

## Details
A flaw was found in the KVM's AMD code for supporting SVM nested virtualization. The flaw occurs when processing the VMCB (virtual machine control block) provided by the L1 guest to spawn/handle a nested guest (L2). Due to improper validation of the "virt_ext" field, this issue could allow a malicious L1 to disable both VMLOAD/VMSAVE intercepts and VLS (Virtual VMLOAD/VMSAVE) for the L2 guest. As a result, the L2 guest would be allowed to read/write physical pages of the host, resulting in a crash of the entire system, leak of sensitive data or potential guest-to-host escape.

## References
- https://www.openwall.com/lists/oss-security/2021/08/16/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1983988
- https://git.kernel.org/pub/scm/virt/kvm/kvm.git/commit/?id=c7dfa4009965a9b2d7b329ee970eb8da0d32f0bc
- https://github.com/torvalds/linux/commit/c7dfa4009965a9b2d7b329ee970eb8da0d32f0bc
