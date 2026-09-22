# [M] rust-vmm linux-loader vulnerable to Out-of-bounds Read

## Summary
Severity: Medium
Advisory: CVE-2022-23523
Aliases: GHSA-52h2-m2cf-9jh6
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-12-13
Source: https://osv.dev/vulnerability/CVE-2022-23523
Type: osv

## Details
In versions prior to 0.8.1, the linux-loader crate uses the offsets and sizes provided in the ELF headers to determine the offsets to read from. If those offsets point beyond the end of the file this could lead to Virtual Machine Monitors using the `linux-loader` crate entering an infinite loop if the ELF header of the kernel they are loading was modified in a malicious manner. This issue has been addressed in 0.8.1. The issue can be mitigated by ensuring that only trusted kernel images are loaded or by verifying that the headers do not point beyond the end of the file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23523.json
- https://github.com/rust-vmm/linux-loader/security/advisories/GHSA-52h2-m2cf-9jh6
- https://nvd.nist.gov/vuln/detail/CVE-2022-23523
- https://github.com/rust-vmm/linux-loader/pull/125
