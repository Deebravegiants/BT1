# [C] FACTION Unauthenticated Custom Extension Upload leads to RCE

## Summary
Severity: Critical
Advisory: CVE-2025-66022
Aliases: GHSA-xr72-2g43-586w
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-66022
Type: osv

## Details
FACTION is a PenTesting Report Generation and Collaboration Framework. Prior to version 1.7.1, an extension execution path in Faction’s extension framework permits untrusted extension code to execute arbitrary system commands on the server when a lifecycle hook is invoked, resulting in remote code execution (RCE) on the host running Faction. Due to a missing authentication check on the /portal/AppStoreDashboard endpoint, an attacker can access the extension management UI and upload a malicious extension without any authentication, making this vulnerability exploitable by unauthenticated users. This issue has been patched in version 1.7.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66022.json
- https://github.com/factionsecurity/faction/security/advisories/GHSA-xr72-2g43-586w
- https://nvd.nist.gov/vuln/detail/CVE-2025-66022
- https://github.com/factionsecurity/faction/commit/c6389f1c76175b7c1c68d1a87b389311b16c62c3
