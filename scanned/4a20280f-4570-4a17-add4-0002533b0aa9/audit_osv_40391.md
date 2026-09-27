# [H] bpf: Fix ld_{abs,ind} failure path analysis in subprogs

## Summary
Severity: High
Advisory: CVE-2026-53090
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53090
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix ld_{abs,ind} failure path analysis in subprogs

Usage of ld_{abs,ind} instructions got extended into subprogs some time
ago via commit 09b28d76eac4 ("bpf: Add abnormal return checks."). These
are only allowed in subprograms when the latter are BTF annotated and
have scalar return types.

The code generator in bpf_gen_ld_abs() has an abnormal exit path (r0=0 +
exit) from legacy cBPF times. While the enforcement is on scalar return
types, the verifier must also simulate the path of abnormal exit if the
packet data load via ld_{abs,ind} failed.

This is currently not the case. Fix it by having the verifier simulate
both success and failure paths, and extend it in similar ways as we do
for tail calls. The success path (r0=unknown, continue to next insn) is
pushed onto stack for later validation and the r0=0 and return to the
caller is done on the fall-through side.

## References
- https://git.kernel.org/stable/c/37ad2bb11e9de92cb7b94548705eeedd87f7d392
- https://git.kernel.org/stable/c/8674e2db06cff6b50f2216eed9a761d15425bb34
- https://git.kernel.org/stable/c/8a800497d9f6c2ec9c2c1ba7b71d0ac2ea7f7bbe
- https://git.kernel.org/stable/c/928d354ae3557e8f755a227e67be88034eb3cd7f
- https://git.kernel.org/stable/c/ce01a4e5cfac7adbe0be565f90cd32ecbb2f8337
- https://git.kernel.org/stable/c/d846d83bdacbd8f14fc45c63b8c1d22608452e1c
- https://git.kernel.org/stable/c/de1055e7f9e67af32b1f3376066272b04e5223c0
- https://git.kernel.org/stable/c/ee861486e377edc55361c08dcbceab3f6b6577bd
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53090.json
- https://access.redhat.com/security/cve/CVE-2026-53090
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53090.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53090
- https://bugzilla.redhat.com/show_bug.cgi?id=2492305
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
