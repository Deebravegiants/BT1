# [M] Improper propagation of permission scheme updates across cluster nodes

## Summary
Severity: Medium
Advisory: CVE-2024-12247
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-12-05
Source: https://osv.dev/vulnerability/CVE-2024-12247
Type: osv

## Details
Mattermost versions 9.7.x <= 9.7.5, 9.8.x <= 9.8.2 and 9.9.x <= 9.9.2 fail to properly propagate permission scheme updates across cluster nodes which allows a user to keep old permissions, even if the permission scheme has been updated.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12247.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12247
