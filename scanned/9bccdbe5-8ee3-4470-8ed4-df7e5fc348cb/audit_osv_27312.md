# [C] CVE-2024-1643

## Summary
Severity: Critical
Advisory: CVE-2024-1643
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-1643
Type: osv

## Details
By knowing an organization's ID, an attacker can join the organization without permission and gain the ability to read and modify all data within that organization. This vulnerability allows unauthorized access and modification of sensitive information, posing a significant security risk. The flaw is due to insufficient verification of user permissions when joining an organization.

## References
- https://huntr.com/bounties/ce2563a2-3d81-4e2e-954e-abecb9332416
- https://github.com/lunary-ai/lunary/compare/v1.2.1...v1.2.2
- https://github.com/lunary-ai/lunary/commit/67eaefe1c77c882c628780940c704a117b561d51
