# [H] CVE-2021-29657

## Summary
Severity: High
Advisory: CVE-2021-29657
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/CVE-2021-29657
Type: osv

## Details
arch/x86/kvm/svm/nested.c in the Linux kernel before 5.11.12 has a use-after-free in which an AMD KVM guest can bypass access control on host OS MSRs when there are nested guests, aka CID-a58d9166a756. This occurs because of a TOCTOU race condition associated with a VMCB12 double fetch in nested_svm_vmrun.

## References
- http://packetstormsecurity.com/files/163324/KVM-nested_svm_vmrun-Double-Fetch.html
- https://security.netapp.com/advisory/ntap-20210902-0008/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2177
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.12
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=a58d9166a756a0f4a6618e4f593232593d6df134
