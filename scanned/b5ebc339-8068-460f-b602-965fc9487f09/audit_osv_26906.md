# [M] CVE-2023-5680

## Summary
Severity: Medium
Advisory: CVE-2023-5680
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/CVE-2023-5680
Type: osv

## Details
If a resolver cache has a very large number of ECS records stored for the same name, the process of cleaning the cache database node for this name can significantly impair query performance. 
This issue affects BIND 9 versions 9.11.3-S1 through 9.11.37-S1, 9.16.8-S1 through 9.16.45-S1, and 9.18.11-S1 through 9.18.21-S1.

## References
- https://kb.isc.org/docs/cve-2023-5680
- https://security.netapp.com/advisory/ntap-20240503-0005/
