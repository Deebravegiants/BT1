# [M] CVE-2021-43056

## Summary
Severity: Medium
Advisory: CVE-2021-43056
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-28
Source: https://osv.dev/vulnerability/CVE-2021-43056
Type: osv

## Details
An issue was discovered in the Linux kernel for powerpc before 5.14.15. It allows a malicious KVM guest to crash the host, when the host is running on Power8, due to an arch/powerpc/kvm/book3s_hv_rmhandlers.S implementation bug in the handling of the SRR1 register values.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AA7EAPPKWG4LMTQQLNNSKATY6ST2KQFE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BBM4FP3IT3JZ2O7EBS7TEOG657N4ZGRE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RRAIS3PG4EV5WFLYESR6FXWM4BJJGWVA/
- https://lore.kernel.org/linuxppc-dev/87pmrtbbdt.fsf%40mpe.ellerman.id.au/T/#u
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.15
- http://www.openwall.com/lists/oss-security/2021/10/28/1
- https://git.kernel.org/linus/cdeb5d7d890e14f3b70e8087e745c4a6a7d9f337
