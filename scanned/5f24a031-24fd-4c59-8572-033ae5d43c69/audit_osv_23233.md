# [M] CVE-2022-45869

## Summary
Severity: Medium
Advisory: CVE-2022-45869
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-30
Source: https://osv.dev/vulnerability/CVE-2022-45869
Type: osv

## Details
A race condition in the x86 KVM subsystem in the Linux kernel through 6.1-rc6 allows guest OS users to cause a denial of service (host OS crash or host OS memory corruption) when nested virtualisation and the TDP MMU are enabled.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=47b0c2e4c220f2251fd8dcfbb44479819c715e15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45869.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-45869
