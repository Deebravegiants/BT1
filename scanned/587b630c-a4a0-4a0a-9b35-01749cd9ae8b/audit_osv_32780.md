# [H] perf/x86/intel: KVM: Mask PEBS_ENABLE loaded for guest with vCPU's value.

## Summary
Severity: High
Advisory: CVE-2025-37936
Ecosystem: Linux
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37936
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.138, >=6.2.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/x86/intel: KVM: Mask PEBS_ENABLE loaded for guest with vCPU's value.

When generating the MSR_IA32_PEBS_ENABLE value that will be loaded on
VM-Entry to a KVM guest, mask the value with the vCPU's desired PEBS_ENABLE
value.  Consulting only the host kernel's host vs. guest masks results in
running the guest with PEBS enabled even when the guest doesn't want to use
PEBS.  Because KVM uses perf events to proxy the guest virtual PMU, simply
looking at exclude_host can't differentiate between events created by host
userspace, and events created by KVM on behalf of the guest.

Running the guest with PEBS unexpectedly enabled typically manifests as
crashes due to a near-infinite stream of #PFs.  E.g. if the guest hasn't
written MSR_IA32_DS_AREA, the CPU will hit page faults on address '0' when
trying to record PEBS events.

The issue is most easily reproduced by running `perf kvm top` from before
commit 7b100989b4f6 ("perf evlist: Remove __evlist__add_default") (after
which, `perf kvm top` effectively stopped using PEBS).	The userspace side
of perf creates a guest-only PEBS event, which intel_guest_get_msrs()
misconstrues a guest-*owned* PEBS event.

Arguably, this is a userspace bug, as enabling PEBS on guest-only events
simply cannot work, and userspace can kill VMs in many other ways (there
is no danger to the host).  However, even if this is considered to be bad
userspace behavior, there's zero downside to perf/KVM restricting PEBS to
guest-owned events.

Note, commit 854250329c02 ("KVM: x86/pmu: Disable guest PEBS temporarily
in two rare situations") fixed the case where host userspace is profiling
KVM *and* userspace, but missed the case where userspace is profiling only
KVM.

## References
- https://git.kernel.org/stable/c/160153cf9e4aa875ad086cc094ce34aac8e13d63
- https://git.kernel.org/stable/c/34b6fa11431aef71045ae5a00d90a7d630597eda
- https://git.kernel.org/stable/c/44ee0afc9d1e7a7c1932698de01362ed80cfc4b5
- https://git.kernel.org/stable/c/58f6217e5d0132a9f14e401e62796916aa055c1b
- https://git.kernel.org/stable/c/86aa62895fc2fb7ab09d7ca40fae8ad09841f66b
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37936.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37936
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
