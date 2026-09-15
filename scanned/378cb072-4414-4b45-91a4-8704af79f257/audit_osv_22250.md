# [H] Command Injection

## Summary
Severity: High
Advisory: CVE-2022-24433
Aliases: GHSA-3f95-r44v-8mrg
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-11
Source: https://osv.dev/vulnerability/CVE-2022-24433
Type: osv

## Details
The package simple-git before 3.3.0 are vulnerable to Command Injection via argument injection. When calling the .fetch(remote, branch, handlerFn) function, both the remote and branch parameters are passed to the git fetch subcommand. By injecting some git options it was possible to get arbitrary command execution.

## References
- https://github.com/steveukx/git-js/releases/tag/simple-git%403.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24433.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-24433
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2421245
- https://snyk.io/vuln/SNYK-JS-SIMPLEGIT-2421199
- https://github.com/steveukx/git-js/pull/767
