# [M] Incomplete validation of kernel object pointers in system calls

## Summary
Severity: Medium
Advisory: CVE-2025-55078
Aliases: GHSA-wcfg-5jpf-hhxq
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/CVE-2025-55078
Type: osv

## Details
In Eclipse ThreadX before version 6.4.3, an attacker can cause a denial of service (crash) by providing a pointer to a reserved or unmapped memory region. Vulnerable system calls had a check of pointers, but that check wasn't verifying whether the pointer is outside the module memory region.

## References
- https://github.com/eclipse-threadx/threadx/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55078.json
- https://github.com/eclipse-threadx/threadx/security/advisories/GHSA-wcfg-5jpf-hhxq
- https://nvd.nist.gov/vuln/detail/CVE-2025-55078
