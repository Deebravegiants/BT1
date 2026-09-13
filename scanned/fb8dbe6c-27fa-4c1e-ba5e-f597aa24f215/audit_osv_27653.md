# [H] Integer wraparound, under-allocation, and heap buffer overflow in Eclipse ThreadX NetX Duo __portable_aligned_alloc()

## Summary
Severity: High
Advisory: CVE-2024-2452
Aliases: GHSA-h963-7vhw-8rpx
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2024-2452
Type: osv

## Details
In Eclipse ThreadX NetX Duo before 6.4.0, if an attacker can control 
parameters of __portable_aligned_alloc() could cause an integer 
wrap-around and an allocation smaller than expected. This could cause 
subsequent heap buffer overflows.

## References
- http://seclists.org/fulldisclosure/2024/May/35
- http://www.openwall.com/lists/oss-security/2024/05/28/1
- https://github.com/eclipse-threadx/netxduo/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2452.json
- https://github.com/eclipse-threadx/netxduo/security/advisories/GHSA-h963-7vhw-8rpx
- https://nvd.nist.gov/vuln/detail/CVE-2024-2452
