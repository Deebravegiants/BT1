# [C] KVM: arm64: nv: Re-translate VNCR before injecting abort

## Summary
Severity: Critical
Advisory: CVE-2026-72278
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72278
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: nv: Re-translate VNCR before injecting abort

KVM faults in the VNCR page with FOLL_WRITE whenever the guest aborts
for a write, similar to how a regular stage-2 mapping is handled. It is
entirely possible that the guest reads from the VNCR before writing to
it, in which case the PFN could only be read-only.

Invalidate the VNCR TLB and re-fetch the translation upon taking a VNCR
abort, allowing the host mapping to be faulted in for write the second
time around. Interestingly enough, this also satisfies the ordering
requirements of FEAT_ETS2/3 between descriptor updates and MMU faults.

## References
- https://git.kernel.org/stable/c/0a5dd8cf4d58ea28da132c2097cd1c525302ac48
- https://git.kernel.org/stable/c/bb645aa0a4caeaf7f9cd32e9a948594d434c1a8f
- https://git.kernel.org/stable/c/ea7a76d7d614b5f82b4d0785f9af3550e860a71a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72278.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72278
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
