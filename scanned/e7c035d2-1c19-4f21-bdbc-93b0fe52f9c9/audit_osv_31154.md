# [H] KVM: Explicitly verify target vCPU is online in kvm_get_vcpu()

## Summary
Severity: High
Advisory: CVE-2024-58083
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58083
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Explicitly verify target vCPU is online in kvm_get_vcpu()

Explicitly verify the target vCPU is fully online _prior_ to clamping the
index in kvm_get_vcpu().  If the index is "bad", the nospec clamping will
generate '0', i.e. KVM will return vCPU0 instead of NULL.

In practice, the bug is unlikely to cause problems, as it will only come
into play if userspace or the guest is buggy or misbehaving, e.g. KVM may
send interrupts to vCPU0 instead of dropping them on the floor.

However, returning vCPU0 when it shouldn't exist per online_vcpus is
problematic now that KVM uses an xarray for the vCPUs array, as KVM needs
to insert into the xarray before publishing the vCPU to userspace (see
commit c5b077549136 ("KVM: Convert the kvm->vcpus array to a xarray")),
i.e. before vCPU creation is guaranteed to succeed.

As a result, incorrectly providing access to vCPU0 will trigger a
use-after-free if vCPU0 is dereferenced and kvm_vm_ioctl_create_vcpu()
bails out of vCPU creation due to an error and frees vCPU0.  Commit
afb2acb2e3a3 ("KVM: Fix vcpu_array[0] races") papered over that issue, but
in doing so introduced an unsolvable teardown conundrum.  Preventing
accesses to vCPU0 before it's fully online will allow reverting commit
afb2acb2e3a3, without re-introducing the vcpu_array[0] UAF race.

## References
- https://git.kernel.org/stable/c/09d50ccf0b2d739db4a485b08afe7520a4402a63
- https://git.kernel.org/stable/c/125da53b3c0c9d7f58353aea0076e9efd6498ba7
- https://git.kernel.org/stable/c/1e7381f3617d14b3c11da80ff5f8a93ab14cfc46
- https://git.kernel.org/stable/c/5cce2ed69b00e022b5cdf0c49c82986abd2941a8
- https://git.kernel.org/stable/c/7c4899239d0f70f88ac42665b3da51678d122480
- https://git.kernel.org/stable/c/ca8da90ed1432ff3d000de4f1e2275d4e7d21b96
- https://git.kernel.org/stable/c/d817e510662fd1c9797952408d94806f97a5fffd
- https://git.kernel.org/stable/c/f2f805ada63b536bc192458a7098388286568ad4
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58083.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58083
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
