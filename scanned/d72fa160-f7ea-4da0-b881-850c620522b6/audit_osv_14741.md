# [H] CVE-2019-11229

## Summary
Severity: High
Advisory: CVE-2019-11229
Aliases: GHSA-hpmr-prr2-cqc4, GO-2022-0846
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-15
Source: https://osv.dev/vulnerability/CVE-2019-11229
Type: osv

## Details
models/repo_mirror.go in Gitea before 1.7.6 and 1.8.x before 1.8-RC3 mishandles mirror repo URL settings, leading to remote code execution.

## References
- https://github.com/go-gitea/gitea/releases/tag/v1.7.6
- https://github.com/go-gitea/gitea/releases/tag/v1.8.0-rc3
- http://packetstormsecurity.com/files/160833/Gitea-1.7.5-Remote-Code-Execution.html
