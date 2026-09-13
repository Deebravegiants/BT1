# [M] KVM: arm64: vgic-v2: Check for non-NULL vCPU in vgic_v2_parse_attr()

## Summary
Severity: Medium
Advisory: CVE-2024-36953
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36953
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: vgic-v2: Check for non-NULL vCPU in vgic_v2_parse_attr()

vgic_v2_parse_attr() is responsible for finding the vCPU that matches
the user-provided CPUID, which (of course) may not be valid. If the ID
is invalid, kvm_get_vcpu_by_id() returns NULL, which isn't handled
gracefully.

Similar to the GICv3 uaccess flow, check that kvm_get_vcpu_by_id()
actually returns something and fail the ioctl if not.

## References
- https://git.kernel.org/stable/c/01981276d64e542c177b243f7c979fee855d5487
- https://git.kernel.org/stable/c/17db92da8be5dd3bf63c01f4109fe47db64fc66f
- https://git.kernel.org/stable/c/3a5b0378ac6776c7c31b18e0f3c1389bd6005e80
- https://git.kernel.org/stable/c/4404465a1bee3607ad90a4c5f9e16dfd75b85728
- https://git.kernel.org/stable/c/6ddb4f372fc63210034b903d96ebbeb3c7195adb
- https://git.kernel.org/stable/c/8d6a1c8e3de36cb0f5e866f1a582b00939e23104
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36953.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36953
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
