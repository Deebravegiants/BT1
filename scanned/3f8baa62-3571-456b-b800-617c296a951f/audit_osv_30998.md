# [H] CVE-2024-57610

## Summary
Severity: High
Advisory: CVE-2024-57610
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-06
Source: https://osv.dev/vulnerability/CVE-2024-57610
Type: osv

## Details
A rate limiting issue in Sylius v2.0.2 allows a remote attacker to perform unrestricted brute-force attacks on user accounts, significantly increasing the risk of account compromise and denial of service for legitimate users. The Supplier's position is that the Sylius core software is not intended to address brute-force attacks; instead, customers deploying a Sylius-based system are supposed to use "firewalls, rate-limiting middleware, or authentication providers" for that functionality.

## References
- https://sylius.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57610.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57610
- https://github.com/Sylius/Sylius
- https://github.com/nca785/CVE-2024-57610
