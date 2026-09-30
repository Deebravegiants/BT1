# [H] KVM: VMX: Bury Intel PT virtualization (guest/host mode) behind CONFIG_BROKEN

## Summary
Severity: High
Advisory: CVE-2024-53135
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53135
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: VMX: Bury Intel PT virtualization (guest/host mode) behind CONFIG_BROKEN

Hide KVM's pt_mode module param behind CONFIG_BROKEN, i.e. disable support
for virtualizing Intel PT via guest/host mode unless BROKEN=y.  There are
myriad bugs in the implementation, some of which are fatal to the guest,
and others which put the stability and health of the host at risk.

For guest fatalities, the most glaring issue is that KVM fails to ensure
tracing is disabled, and *stays* disabled prior to VM-Enter, which is
necessary as hardware disallows loading (the guest's) RTIT_CTL if tracing
is enabled (enforced via a VMX consistency check).  Per the SDM:

  If the logical processor is operating with Intel PT enabled (if
  IA32_RTIT_CTL.TraceEn = 1) at the time of VM entry, the "load
  IA32_RTIT_CTL" VM-entry control must be 0.

On the host side, KVM doesn't validate the guest CPUID configuration
provided by userspace, and even worse, uses the guest configuration to
decide what MSRs to save/load at VM-Enter and VM-Exit.  E.g. configuring
guest CPUID to enumerate more address ranges than are supported in hardware
will result in KVM trying to passthrough, save, and load non-existent MSRs,
which generates a variety of WARNs, ToPA ERRORs in the host, a potential
deadlock, etc.

## References
- https://git.kernel.org/stable/c/aa0d42cacf093a6fcca872edc954f6f812926a17
- https://git.kernel.org/stable/c/b8a1d572478b6f239061ee9578b2451bf2f021c2
- https://git.kernel.org/stable/c/b91bb0ce5cd7005b376eac690ec664c1b56372ec
- https://git.kernel.org/stable/c/c3742319d021f5aa3a0a8c828485fee14753f6de
- https://git.kernel.org/stable/c/d28b059ee4779b5102c5da6e929762520510e406
- https://git.kernel.org/stable/c/d4b42f926adcce4e5ec193c714afd9d37bba8e5b
- https://git.kernel.org/stable/c/e6716f4230a8784957273ddd27326264b27b9313
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53135.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53135
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
