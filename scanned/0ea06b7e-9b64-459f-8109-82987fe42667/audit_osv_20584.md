# [H] CVE-2021-35342

## Summary
Severity: High
Advisory: CVE-2021-35342
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/CVE-2021-35342
Type: osv

## Details
The useradm service 1.14.0 (in Northern.tech Mender Enterprise 2.7.x before 2.7.1) and 1.13.0 (in Northern.tech Mender Enterprise 2.6.x before 2.6.1) allows users to access the system with their JWT token after logout, because of missing invalidation (if the JWT verification cache is enabled).

## References
- https://mender.io/blog/cve-2021-35342-useradm-logout-vulnerabililty
- https://northern.tech/our-products
