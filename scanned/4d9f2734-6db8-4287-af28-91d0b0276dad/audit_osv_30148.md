# [H] KVM: nSVM: Ignore nCR3[4:0] when loading PDPTEs from memory

## Summary
Severity: High
Advisory: CVE-2024-50115
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50115
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: nSVM: Ignore nCR3[4:0] when loading PDPTEs from memory

Ignore nCR3[4:0] when loading PDPTEs from memory for nested SVM, as bits
4:0 of CR3 are ignored when PAE paging is used, and thus VMRUN doesn't
enforce 32-byte alignment of nCR3.

In the absolute worst case scenario, failure to ignore bits 4:0 can result
in an out-of-bounds read, e.g. if the target page is at the end of a
memslot, and the VMM isn't using guard pages.

Per the APM:

  The CR3 register points to the base address of the page-directory-pointer
  table. The page-directory-pointer table is aligned on a 32-byte boundary,
  with the low 5 address bits 4:0 assumed to be 0.

And the SDM's much more explicit:

  4:0    Ignored

Note, KVM gets this right when loading PDPTRs, it's only the nSVM flow
that is broken.

## References
- https://git.kernel.org/stable/c/2c4adc9b192a0815fe58a62bc0709449416cc884
- https://git.kernel.org/stable/c/426682afec71ea3f889b972d038238807b9443e4
- https://git.kernel.org/stable/c/58cb697d80e669c56197f703e188867c8c54c494
- https://git.kernel.org/stable/c/6876793907cbe19d42e9edc8c3315a21e06c32ae
- https://git.kernel.org/stable/c/76ce386feb14ec9a460784fcd495d8432acce7a5
- https://git.kernel.org/stable/c/f559b2e9c5c5308850544ab59396b7d53cfc67bd
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50115.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
