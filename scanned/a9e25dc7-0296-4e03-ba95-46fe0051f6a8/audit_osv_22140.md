# [M] Speculative execution attacks in KVM VMX

## Summary
Severity: Medium
Advisory: CVE-2022-2196
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2023-01-09
Source: https://osv.dev/vulnerability/CVE-2022-2196
Type: osv

## Details
A regression exists in the Linux Kernel within KVM: nVMX that allowed for speculative execution attacks. L2 can carry out Spectre v2 attacks on L1 due to L1 thinking it doesn't need retpolines or IBPB after running L2 due to KVM (L0) advertising eIBRS support to L1. An attacker at L2 with code execution can execute code on an indirect branch on the host machine. We recommend upgrading to Kernel 6.2 or past commit 2e7eab81425a

## References
- https://git.kernel.org/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=2e7eab81425ad6c875f2ed47c0ce01e78afc38a5
- https://kernel.dance/#2e7eab81425a
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2196.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2196
- https://security.netapp.com/advisory/ntap-20230223-0002/
