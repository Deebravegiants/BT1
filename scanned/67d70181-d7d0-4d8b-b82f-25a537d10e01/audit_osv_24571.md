# [M] CVE-2023-23005

## Summary
Severity: Medium
Advisory: CVE-2023-23005
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/CVE-2023-23005
Type: osv

## Details
In the Linux kernel before 6.2, mm/memory-tiers.c misinterprets the alloc_memory_type return value (expects it to be NULL in the error case, whereas it is actually an error pointer). NOTE: this is disputed by third parties because there are no realistic cases in which a user can cause the alloc_memory_type error case to be reached.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23005.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23005
- https://bugzilla.suse.com/show_bug.cgi?id=1208844#c2
- https://github.com/torvalds/linux/commit/4a625ceee8a0ab0273534cb6b432ce6b331db5ee
