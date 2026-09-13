# [C] OpenObserve Unauthorized Access Vulnerability in Users API

## Summary
Severity: Critical
Advisory: CVE-2024-25106
Aliases: GHSA-3m5f-9m66-xgp7
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/CVE-2024-25106
Type: osv

## Details
OpenObserve is a observability platform built specifically for logs, metrics, traces, analytics, designed to work at petabyte scale. A critical vulnerability has been identified in the "/api/{org_id}/users/{email_id}" endpoint. This vulnerability allows any authenticated user within an organization to remove any other user from that same organization, irrespective of their respective roles. This includes the ability to remove users with "Admin" and "Root" roles. By enabling any organizational member to unilaterally alter the user base, it opens the door to unauthorized access and can cause considerable disruptions in operations. The core of the vulnerability lies in the `remove_user_from_org` function in the user management system. This function is designed to allow organizational users to remove members from their organization. The function does not check if the user initiating the request has the appropriate administrative privileges to remove a user. Any user who is part of the organization, irrespective of their role, can remove any other user, including those with higher privileges. This vulnerability is categorized as an Authorization issue leading to Unauthorized User Removal. The impact is severe, as it compromises the integrity of user management within organizations. By exploiting this vulnerability, any user within an organization, without the need for administrative privileges, can remove critical users, including "Admins" and "Root" users. This could result in unauthorized system access, administrative lockout, or operational disruptions. Given that user accounts are typically created by "Admins" or "Root" users, this vulnerability can be exploited by any user who has been granted access to an organization, thereby posing a critical risk to the security and operational stability of the application. This issue has been addressed in release version 0.8.0. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25106.json
- https://github.com/openobserve/openobserve/security/advisories/GHSA-3m5f-9m66-xgp7
- https://nvd.nist.gov/vuln/detail/CVE-2024-25106
