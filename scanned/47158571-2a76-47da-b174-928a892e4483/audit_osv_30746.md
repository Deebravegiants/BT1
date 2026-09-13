# [H] OpenObserve Improper Authorization Allows Admin User to Remove Root User

## Summary
Severity: High
Advisory: CVE-2024-55954
Aliases: GHSA-m8gj-6r85-3r6m
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-01-16
Source: https://osv.dev/vulnerability/CVE-2024-55954
Type: osv

## Details
OpenObserve is a cloud-native observability platform. A vulnerability in the user management endpoint `/api/{org_id}/users/{email_id}` allows an "Admin" role user to remove a "Root" user from the organization. This violates the intended privilege hierarchy, enabling a non-root user to remove the highest-privileged account. Due to insufficient role checks, the `remove_user_from_org` function does not prevent an "Admin" user from removing a "Root" user. As a result, an attacker with an "Admin" role can remove critical "Root" users, potentially gaining effective full control by eliminating the highest-privileged accounts. The `DELETE /api/{org_id}/users/{email_id}` endpoint is affected. This issue has been addressed in release version `0.14.1` and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/gaby/openobserve/blob/main/src/service/users.rs#L631
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55954.json
- https://github.com/openobserve/openobserve/security/advisories/GHSA-m8gj-6r85-3r6m
- https://nvd.nist.gov/vuln/detail/CVE-2024-55954
