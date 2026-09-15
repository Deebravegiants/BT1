# [M] Kernel: ksmbd memory exhaustion denial-of-service vulnerability

## Summary
Severity: Medium
Advisory: CVE-2023-2593
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-30
Source: https://osv.dev/vulnerability/CVE-2023-2593
Type: osv

## Details
A flaw exists within the Linux kernel's handling of new TCP connections. The issue results from the lack of memory release after its effective lifetime. This vulnerability allows an unauthenticated attacker to create a denial of service condition on the system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/
- https://lore.kernel.org/lkml/CAH2r5msyEy20e=FBx6wPWWc3kXzNR4b+zHshSqidRdFKVf_7Jg@mail.gmail.com/
- https://access.redhat.com/security/cve/CVE-2023-2593
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2593.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2593
- https://bugzilla.redhat.com/show_bug.cgi?id=2384787
