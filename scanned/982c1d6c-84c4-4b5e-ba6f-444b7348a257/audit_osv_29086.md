# [H] KVM: SVM: WARN on vNMI + NMI window iff NMIs are outright masked

## Summary
Severity: High
Advisory: CVE-2024-39483
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39483
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.34, >=6.7.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: WARN on vNMI + NMI window iff NMIs are outright masked

When requesting an NMI window, WARN on vNMI support being enabled if and
only if NMIs are actually masked, i.e. if the vCPU is already handling an
NMI.  KVM's ABI for NMIs that arrive simultanesouly (from KVM's point of
view) is to inject one NMI and pend the other.  When using vNMI, KVM pends
the second NMI simply by setting V_NMI_PENDING, and lets the CPU do the
rest (hardware automatically sets V_NMI_BLOCKING when an NMI is injected).

However, if KVM can't immediately inject an NMI, e.g. because the vCPU is
in an STI shadow or is running with GIF=0, then KVM will request an NMI
window and trigger the WARN (but still function correctly).

Whether or not the GIF=0 case makes sense is debatable, as the intent of
KVM's behavior is to provide functionality that is as close to real
hardware as possible.  E.g. if two NMIs are sent in quick succession, the
probability of both NMIs arriving in an STI shadow is infinitesimally low
on real hardware, but significantly larger in a virtual environment, e.g.
if the vCPU is preempted in the STI shadow.  For GIF=0, the argument isn't
as clear cut, because the window where two NMIs can collide is much larger
in bare metal (though still small).

That said, KVM should not have divergent behavior for the GIF=0 case based
on whether or not vNMI support is enabled.  And KVM has allowed
simultaneous NMIs with GIF=0 for over a decade, since commit 7460fb4a3400
("KVM: Fix simultaneous NMIs").  I.e. KVM's GIF=0 handling shouldn't be
modified without a *really* good reason to do so, and if KVM's behavior
were to be modified, it should be done irrespective of vNMI support.

## References
- https://git.kernel.org/stable/c/1d87cf2eba46deaff6142366127f2323de9f84d1
- https://git.kernel.org/stable/c/b4bd556467477420ee3a91fbcba73c579669edc6
- https://git.kernel.org/stable/c/f79edaf7370986d73d204b36c50cc563a4c0f356
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39483.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39483
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
