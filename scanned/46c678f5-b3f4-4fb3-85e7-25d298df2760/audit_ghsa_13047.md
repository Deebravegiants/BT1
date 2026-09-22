# [H] Argo CD web terminal session doesn't expire

## Summary
Severity: High
Advisory: GHSA-c8xw-vjgf-94hr
CVE: CVE-2023-40025
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-c8xw-vjgf-94hr
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.6.0 <2.6.14
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.7.0 <2.7.12
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.8.0 <2.8.1
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.0.0-20230718200744-12a5a7a70d6e <2.0.0-20230821201509-e047efa8f951

## Details
### Impact
All versions of Argo CD starting from v2.6.0 have a bug where open web terminal sessions do not expire. This bug allows users to send any websocket messages even if the token has already expired. The most straightforward scenario is when a user opens the terminal view and leaves it open for an extended period. This allows the user to view sensitive information even when they should have been logged out already.

### Patches
A patch for this vulnerability has been released in the following Argo CD version:

* v2.6.14
* v2.7.12
* v2.8.1

### Workarounds
The only way to completely resolve the issue is to upgrade.

#### Mitigations
Disable web-based terminal or define RBAC rules to it
[https://argo-cd.readthedocs.io/en/latest/operator-manual/web_based_terminal/](https://argo-cd.readthedocs.io/en/latest/operator-manual/web_based_terminal/)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

### Credits

Thank you to bean.zhang (@zhlu32 ) of HIT-IDS ChunkL Team who discovered the issue and reported it confidentially according to our [guidelines](https://github.com/argoproj/argo-cd/blob/master/SECURITY.md#reporting-a-vulnerability).

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-c8xw-vjgf-94hr
- https://nvd.nist.gov/vuln/detail/CVE-2023-40025
- https://github.com/argoproj/argo-cd/commit/e047efa8f9518c54d00d2e4493b64bc4dba98478
- https://github.com/argoproj/argo-cd
