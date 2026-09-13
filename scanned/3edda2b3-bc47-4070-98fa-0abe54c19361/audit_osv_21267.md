# [C] CVE-2021-41556

## Summary
Severity: Critical
Advisory: CVE-2021-41556
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-07-28
Source: https://osv.dev/vulnerability/CVE-2021-41556
Type: osv

## Details
sqclass.cpp in Squirrel through 2.2.5 and 3.x through 3.1 allows an out-of-bounds read (in the core interpreter) that can lead to Code Execution. If a victim executes an attacker-controlled squirrel script, it is possible for the attacker to break out of the squirrel script sandbox even if all dangerous functionality such as File System functions has been disabled. An attacker might abuse this bug to target (for example) Cloud services that allow customization via SquirrelScripts, or distribute malware through video games that embed a Squirrel Engine.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BV7SJJ44AGAX4ILIVPREIXPJ2GOG3FKV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M3FQILX7UUEERSDPMZP3MKGTMY2E7ESU/
- http://www.squirrel-lang.org/#download
- https://github.com/albertodemichelis/squirrel/commit/23a0620658714b996d20da3d4dd1a0dcf9b0bd98
- https://www.sonarsource.com/blog/squirrel-vm-sandbox-escape/
- https://blog.sonarsource.com/squirrel-vm-sandbox-escape/
