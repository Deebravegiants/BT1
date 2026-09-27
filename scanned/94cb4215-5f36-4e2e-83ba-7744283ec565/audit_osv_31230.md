# [M] Limited DoS due to permitting creating users with user-defined IDs

## Summary
Severity: Medium
Advisory: CVE-2024-6428
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-07-03
Source: https://osv.dev/vulnerability/CVE-2024-6428
Type: osv

## Details
Mattermost versions 9.8.0, 9.7.x <= 9.7.4, 9.6.x <= 9.6.2, 9.5.x <= 9.5.5 fail to prevent specifying a RemoteId when creating a new user which allows an attacker to specify both a remoteId and the user ID, resulting in creating a user with a user-defined user ID. This can cause some broken functionality in User Management such administrative actions against the user not working.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6428.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6428
