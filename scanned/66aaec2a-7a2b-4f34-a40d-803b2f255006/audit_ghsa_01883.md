# [H] GitLab auth uses full name instead of username as user ID, allowing impersonation

## Summary
Severity: High
Advisory: GHSA-627p-rr78-99rj
CVE: CVE-2020-5415
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-627p-rr78-99rj
Type: github-advisory

## Affected
- Go: `github.com/concourse/concourse` — affected >=6.4.0 <6.4.1
- Go: `github.com/concourse/concourse` — affected >=1.6.1 <6.3.1
- Go: `github.com/concourse/dex` — affected >=6.4.0 <6.4.1
- Go: `github.com/concourse/dex` — affected >=0.0.0 <6.3.1
- Go: `github.com/concourse/dex` — affected >=0 <0.0.0-20200730150203-821b48abfd88
- Go: `github.com/concourse/concourse` — affected >=0 <0.0.0-20200730151558-b00d1c8d8576
- Go: `github.com/concourse/concourse` — affected >=0.0.0 <1.6.1-0.20200730151558-b00d1c8d8576

## Details
### Impact

Installations which use the GitLab auth connector are vulnerable to identity spoofing by way of configuring a GitLab account with the same full name as another GitLab user who is granted access to a Concourse team by having their full name listed under `users` in the team configuration or given to the `--gitlab-user` flag.

See the [GitLab auth docs](https://concourse-ci.org/gitlab-auth.html) for details.

Concourse installations which do not configure the GitLab auth connector are not affected.

### Patches

Concourse [v6.3.1](https://github.com/concourse/concourse/releases/tag/v6.3.1) and [v6.4.1](https://github.com/concourse/concourse/releases/tag/v6.4.1) were both released with a fix on August 4th, 2020.

Both versions change the GitLab connector to use the username, rather than the full name. This was always the intent, and the previous behavior was originally reported as a bug (concourse/dex#7) prior to being reported as a security issue.

Any Concourse teams which configure GitLab users will have to switch each user from their full name to their username upon upgrading to these versions.

### Workarounds

GitLab groups do not have this vulnerability, so GitLab users may be moved into groups which are then configured in the Concourse team.

### References

* concourse/dex#12: PR with the fix

### For more information

If you have any questions or comments about this advisory, you may reach us privately at [concourseteam+security@gmail.com](mailto:concourseteam+security@gmail.com).

## References
- https://github.com/concourse/concourse/security/advisories/GHSA-627p-rr78-99rj
- https://nvd.nist.gov/vuln/detail/CVE-2020-5415
- https://tanzu.vmware.com/security/cve-2020-5415
