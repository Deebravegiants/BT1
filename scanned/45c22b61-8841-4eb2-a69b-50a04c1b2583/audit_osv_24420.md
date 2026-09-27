# [M] Spectre v2 SMT mitigations problem in Linux kernel

## Summary
Severity: Medium
Advisory: CVE-2023-1998
Aliases: GHSA-mj4w-6495-6crx
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-04-21
Source: https://osv.dev/vulnerability/CVE-2023-1998
Type: osv

## Details
The Linux kernel allows userspace processes to enable mitigations by calling prctl with PR_SET_SPECULATION_CTRL which disables the speculation feature as well as by using seccomp. We had noticed that on VMs of at least one major cloud provider, the kernel still left the victim process exposed to attacks in some cases even after enabling the spectre-BTI mitigation with prctl. The same behavior can be observed on a bare-metal machine when forcing the mitigation to IBRS on boot command line.

This happened because when plain IBRS was enabled (not enhanced IBRS), the kernel had some logic that determined that STIBP was not needed. The IBRS bit implicitly protects against cross-thread branch target injection. However, with legacy IBRS, the IBRS bit was cleared on returning to userspace, due to performance reasons, which disabled the implicit STIBP and left userspace threads vulnerable to cross-thread branch target injection against which STIBP protects.

## References
- https://git.kernel.org/
- https://kernel.dance/#6921ed9049bc7457f66c1596c5b78aec0dae4a9d
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1998.json
- https://github.com/google/security-research/security/advisories/GHSA-mj4w-6495-6crx
- https://nvd.nist.gov/vuln/detail/CVE-2023-1998
- https://github.com/torvalds/linux/commit/6921ed9049bc7457f66c1596c5b78aec0dae4a9d
