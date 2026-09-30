# [H] User authorization bug leading to privilege escalation in warpgate

## Summary
Severity: High
Advisory: CVE-2023-48712
Aliases: GHSA-c94j-vqr5-3mxr
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-24
Source: https://osv.dev/vulnerability/CVE-2023-48712
Type: osv

## Details
Warpgate is an open source SSH, HTTPS and MySQL bastion host for Linux. In affected versions there is a privilege escalation vulnerability through a non-admin user's account. Limited users can impersonate another user's account if only single-factor authentication is configured. If a user knows an admin username, opens the login screen and attempts to authenticate with an incorrect password they can subsequently enter a valid non-admin username and password they will be logged in as the admin user. All installations prior to version 0.9.0 are affected. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48712.json
- https://github.com/warp-tech/warpgate/security/advisories/GHSA-c94j-vqr5-3mxr
- https://nvd.nist.gov/vuln/detail/CVE-2023-48712
- https://github.com/warp-tech/warpgate/commit/e3b26b2699257b9482dce2e9157bd9b5e05d9c76
