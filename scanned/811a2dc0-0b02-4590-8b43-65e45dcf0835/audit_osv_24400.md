# [M] CVE-2023-1637

## Summary
Severity: Medium
Advisory: CVE-2023-1637
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-1637
Type: osv

## Details
A flaw that boot CPU could be vulnerable for the speculative execution behavior kind of attacks in the Linux kernel X86 CPU Power management options functionality was found in the way user resuming CPU from suspend-to-RAM. A local user could use this flaw to potentially get unauthorized access to some memory of the CPU similar to the speculative execution behavior kind of attacks.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e2a1256b17b16f9b9adf1b6fea56819e7b68e463
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1637.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1637
- https://sourceware.org/bugzilla/show_bug.cgi?id=27398
