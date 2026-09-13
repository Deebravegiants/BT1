# [M] CVE-2021-22895

## Summary
Severity: Medium
Advisory: CVE-2021-22895
Aliases: GHSA-qpgp-vf4p-wcw5
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-06-11
Source: https://osv.dev/vulnerability/CVE-2021-22895
Type: osv

## Details
Nextcloud Desktop Client before 3.3.1 is vulnerable to improper certificate validation due to lack of SSL certificate verification when using the "Register with a Provider" flow.

## References
- https://github.com/nextcloud/desktop/releases/tag/v3.1.3
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-qpgp-vf4p-wcw5
- https://www.debian.org/security/2021/dsa-4974
- https://hackerone.com/reports/903424
- https://github.com/nextcloud/desktop/pull/2926
