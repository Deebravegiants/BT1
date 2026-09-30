# [C] KVM: arm64: nv: Respect read-only PFN when mapping L1 VNCR

## Summary
Severity: Critical
Advisory: CVE-2026-72279
Ecosystem: Linux
CVSS: 9.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72279
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: nv: Respect read-only PFN when mapping L1 VNCR

KVM currently maps the L1 VNCR into the host stage-1 by relying entirely
on the permissions of the guest stage-1. At the same time, it is
entirely possible that the backing PFN is read-only (e.g. RO memslot),
meaning that the L1 VNCR should use at most a read-only mapping.

Cache the writability of the PFN in the VNCR TLB and use it to constrain
the resulting fixmap permissions. Promote VNCR permission faults to an
SEA in the case where the guest attempts to write to a read-only
endpoint. Conveniently, this also plugs a page leak found by Sashiko [*]
resulting from the early return for a read-only PFN.

## References
- https://git.kernel.org/stable/c/2684e02bac41c5220f6c1ab2bdcc957b71812977
- https://git.kernel.org/stable/c/5c50db5bcbb9073cb2fd97be51b962de92f429e9
- https://git.kernel.org/stable/c/d35defbdfcb15296ebe28968ad7452c1a8c11cea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72279.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
