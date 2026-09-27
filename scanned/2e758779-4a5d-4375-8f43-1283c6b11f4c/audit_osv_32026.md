# [C] Coolify OS Command Injection Vulnerability in SSH Command Generation

## Summary
Severity: Critical
Advisory: CVE-2025-22605
Aliases: GHSA-9wqm-fg79-4748
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2025-01-24
Source: https://osv.dev/vulnerability/CVE-2025-22605
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Starting in version 4.0.0-beta.18 and prior to 4.0.0-beta.253, a vulnerability in the execution of commands on remote servers allows an authenticated user to execute arbitrary code on the local Coolify container, gaining access to data and private keys or tokens of other users/teams. The ability to inject malicious commands into the Coolify container gives authenticated attackers the ability to fully retrieve and control the data and availability of the software. Centrally hosted Coolify instances (open registration and/or multiple teams with potentially untrustworthy users) are especially at risk, as sensitive data of all users and connected servers can be leaked by any user. Additionally, attackers are able to modify the running software, potentially deploying malicious images to remote nodes or generally changing its behavior. Version 4.0.0-beta.253 patches this issue.

## References
- https://github.com/coollabsio/coolify/blob/40a239ddda3fc919f57a052d7b52b8e1a6696b81/bootstrap/helpers/remoteProcess.php#L70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22605.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-9wqm-fg79-4748
- https://nvd.nist.gov/vuln/detail/CVE-2025-22605
- https://github.com/coollabsio/coolify/commit/353245bb7de9680f238bae30443af1696bc977b0
- https://github.com/coollabsio/coolify/pull/1524
- https://github.com/coollabsio/coolify/pull/1625
