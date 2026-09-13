# [M] Lif Auth Server vulnerable to uncontrolled data in path expression

## Summary
Severity: Medium
Advisory: CVE-2023-49801
Aliases: GHSA-3v77-pvqq-qg3f
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-49801
Type: osv

## Details
Lif Auth Server is a server for validating logins, managing information, and account recovery for Lif Accounts. The issue relates to the `get_pfp` and `get_banner` routes on Auth Server. The issue is that there is no check to ensure that the file that Auth Server is receiving through these URLs is correct. This could allow an attacker access to files they shouldn't have access to. This issue has been patched in version 1.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49801.json
- https://github.com/Lif-Platforms/Lif-Auth-Server/security/advisories/GHSA-3v77-pvqq-qg3f
- https://nvd.nist.gov/vuln/detail/CVE-2023-49801
- https://github.com/Lif-Platforms/Lif-Auth-Server/commit/c235bcc2ee65e4a0dfb10284cf2cbc750213efeb
