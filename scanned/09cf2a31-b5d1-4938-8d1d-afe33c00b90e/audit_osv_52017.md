# [M] CVE-2021-46967

## Summary
Severity: Medium
Advisory: CVE-2021-46967
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46967
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

vhost-vdpa: fix vm_flags for virtqueue doorbell mapping

The virtqueue doorbell is usually implemented via registeres but we
don't provide the necessary vma->flags like VM_PFNMAP. This may cause
several issues e.g when userspace tries to map the doorbell via vhost
IOTLB, kernel may panic due to the page is not backed by page
structure. This patch fixes this by setting the necessary
vm_flags. With this patch, try to map doorbell via IOTLB will fail
with bad address.

## References
- https://git.kernel.org/stable/c/3a3e0fad16d40a2aa68ddf7eea4acdf48b22dd44
- https://git.kernel.org/stable/c/3b8b6399666a29daa30b0bb3f5c9e3fc81c5a6a6
- https://git.kernel.org/stable/c/93dbbf20e3ffad14f04227a0b7105f6e6f0387ce
- https://git.kernel.org/stable/c/940230a5c31e2714722aee04c521a21f484b4df7
