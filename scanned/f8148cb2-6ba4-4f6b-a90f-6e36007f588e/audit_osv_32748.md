# [H] KVM: arm64: Tear down vGIC on failed vCPU creation

## Summary
Severity: High
Advisory: CVE-2025-37849
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37849
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Tear down vGIC on failed vCPU creation

If kvm_arch_vcpu_create() fails to share the vCPU page with the
hypervisor, we propagate the error back to the ioctl but leave the
vGIC vCPU data initialised. Note only does this leak the corresponding
memory when the vCPU is destroyed but it can also lead to use-after-free
if the redistributor device handling tries to walk into the vCPU.

Add the missing cleanup to kvm_arch_vcpu_create(), ensuring that the
vGIC vCPU structures are destroyed on error.

## References
- https://git.kernel.org/stable/c/07476e0d932afc53c05468076393ac35d0b4999e
- https://git.kernel.org/stable/c/2480326eba8ae9ccc5e4c3c2dc8d407db68e3c52
- https://git.kernel.org/stable/c/250f25367b58d8c65a1b060a2dda037eea09a672
- https://git.kernel.org/stable/c/5085e02362b9948f82fceca979b8f8e12acb1cc5
- https://git.kernel.org/stable/c/c322789613407647a05ff5c451a7bf545fb34e73
- https://git.kernel.org/stable/c/f1e9087abaeedec9bf2894a282ee4f0d8383f299
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37849.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37849
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
