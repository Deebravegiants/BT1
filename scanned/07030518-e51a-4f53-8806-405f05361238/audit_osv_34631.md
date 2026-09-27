# [C] JumpServer Connection Token Leak Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-62712
Aliases: GHSA-6ghx-6vpv-3wg7
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-62712
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. In JumpServer versions prior to v3.10.20-lts and v4.10.11-lts, an authenticated, non-privileged user can retrieve connection tokens belonging to other users via the super-connection API endpoint (/api/v1/authentication/super-connection-token/). When accessed from a web browser, this endpoint returns connection tokens created by all users instead of restricting results to tokens owned by or authorized for the requester. An attacker who obtains these tokens can use them to initiate connections to managed assets on behalf of the original token owners, resulting in unauthorized access and privilege escalation across sensitive systems. This vulnerability is fixed in v3.10.20-lts and v4.10.11-lts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62712.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-6ghx-6vpv-3wg7
- https://nvd.nist.gov/vuln/detail/CVE-2025-62712
- https://github.com/jumpserver/jumpserver/commit/453ad331eec9d9667a38de735d6612608e558491
