# [M] CVE-2022-3108

## Summary
Severity: Medium
Advisory: CVE-2022-3108
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3108
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. kfd_parse_subtype_iolink in drivers/gpu/drm/amd/amdkfd/kfd_crat.c lacks check of the return value of kmemdup().

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=abfaf0eee97925905e742aa3b0b72e04a918fa9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3108.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3108
- https://bugzilla.redhat.com/show_bug.cgi?id=2153052
