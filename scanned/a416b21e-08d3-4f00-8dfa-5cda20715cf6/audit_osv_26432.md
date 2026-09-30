# [H] KVM: s390/diag: fix racy access of physical cpu number in diag 9c handler

## Summary
Severity: High
Advisory: CVE-2023-53205
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53205
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390/diag: fix racy access of physical cpu number in diag 9c handler

We do check for target CPU == -1, but this might change at the time we
are going to use it. Hold the physical target CPU in a local variable to
avoid out-of-bound accesses to the cpu arrays.

## References
- https://git.kernel.org/stable/c/0bc380beb78aa352eadbc21d934dd9606fcee808
- https://git.kernel.org/stable/c/86bfb18bad60fc468e5f112cbbd918462a8dd435
- https://git.kernel.org/stable/c/a9ccf140a2a03a0ae82be4bdfbdd17bdaea72ff5
- https://git.kernel.org/stable/c/dc7e0192c470a53d847c79a2796f9ac429477a26
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53205.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53205
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
