# [C] Path traversal in Sandboxie

## Summary
Severity: Critical
Advisory: CVE-2024-49360
Aliases: GHSA-4chj-3c28-gvmp
CVSS: 9.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-49360
Type: osv

## Details
Sandboxie is a sandbox-based isolation software for 32-bit and 64-bit Windows NT-based operating systems. An authenticated user (**UserA**) with no privileges is authorized to read all files created in sandbox belonging to other users in the sandbox folders `C:\Sandbox\UserB\xxx`. An authenticated attacker who can use `explorer.exe` or `cmd.exe` outside any sandbox can read other users' files in `C:\Sandbox\xxx`. By default in Windows 7+, the `C:\Users\UserA` folder is not readable by **UserB**.
All files edited or created during the sandbox processing are affected by the vulnerability. All files in C:\Users are safe. If `UserB` runs a cmd in a sandbox, he will be able to access `C:\Sandox\UserA`. In addition, if **UserB** create a folder `C:\Sandbox\UserA` with malicious ACLs, when **UserA** will user the sandbox, Sandboxie doesn't reset ACLs ! This issue has not yet been fixed. Users are advised to limit access to their systems using Sandboxie.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49360.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-4chj-3c28-gvmp
- https://nvd.nist.gov/vuln/detail/CVE-2024-49360
