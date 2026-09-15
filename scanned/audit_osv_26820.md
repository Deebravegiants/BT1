# [H] KVM: s390: pv: fix index value of replaced ASCE

## Summary
Severity: High
Advisory: CVE-2023-54092
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54092
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.190, >=5.11.0 <5.15.124, >=5.16.0 <6.1.43, >=6.0.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: s390: pv: fix index value of replaced ASCE

The index field of the struct page corresponding to a guest ASCE should
be 0. When replacing the ASCE in s390_replace_asce(), the index of the
new ASCE should also be set to 0.

Having the wrong index might lead to the wrong addresses being passed
around when notifying pte invalidations, and eventually to validity
intercepts (VM crash) if the prefix gets unmapped and the notifier gets
called with the wrong address.

## References
- https://git.kernel.org/stable/c/017f686bcb536ff23d49c143fdf9d1fd89a9a924
- https://git.kernel.org/stable/c/49a2686adddebe1ae76b4d368383208656ef6606
- https://git.kernel.org/stable/c/8e635da0e0d3cb45e32fa79b36218fb98281bc10
- https://git.kernel.org/stable/c/c2fceb59bbda16468bda82b002383bff59de89ab
- https://git.kernel.org/stable/c/f1c7a776338f2ac5e34da40e58fe9f33ea390a5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54092.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54092
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
