# [H] KVM: s390: pci: fix GAIT table indexing due to double-scaling pointer arithmetic

## Summary
Severity: High
Advisory: CVE-2026-52968
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52968
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: pci: fix GAIT table indexing due to double-scaling pointer arithmetic

kvm_s390_pci_aif_enable(), kvm_s390_pci_aif_disable(), and
aen_host_forward() index the GAIT by manually multiplying the index
with sizeof(struct zpci_gaite).

Since aift->gait is already a struct zpci_gaite pointer, this
double-scales the offset, accessing element aisb*16 instead of aisb.

This causes out-of-bounds accesses when aisb >= 32 (with
ZPCI_NR_DEVICES=512)

Fix by removing the erroneous sizeof multiplication.

## References
- https://git.kernel.org/stable/c/11b8ff5b930b351dd1f6f088dce0beb027ac92d0
- https://git.kernel.org/stable/c/16d990a15491cf76cd6eef0846e1b4100e63261a
- https://git.kernel.org/stable/c/31a9d9f9942885aae356a1a57c79e82c5b5b0828
- https://git.kernel.org/stable/c/a99a25db131ece5e6c0f7632da606de631efe4f2
- https://git.kernel.org/stable/c/b22a2da8792a7bfe743c1a922e77fa499ddedbe8
- https://git.kernel.org/stable/c/e7216651b94e92e5433fb2f54b77864642b4ea48
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52968.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52968
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
