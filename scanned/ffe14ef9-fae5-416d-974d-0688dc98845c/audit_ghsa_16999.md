# [M] Argo CD vulnerable to a Denial of Service via malicious jqPathExpressions in ignoreDifferences

## Summary
Severity: Medium
Advisory: GHSA-9m6p-x4h2-6frq
CVE: CVE-2024-32476
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-9m6p-x4h2-6frq
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.10.0 <2.10.8
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.9.0 <2.9.13
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.8.17

## Details
### Impact
DoS vuln via OOM using jq in ignoreDifferences.

```
ignoreDifferences:
    - group: apps
       kind: Deployment
       jqPathExpressions: 
	    - 'until(true == false; [.] + [1])'
```

### Patches
A patch for this vulnerability has been released in the following Argo CD versions:

v2.10.8
v2.9.13
v2.8.17

### For more information
If you have any questions or comments about this advisory:

Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

Credits
This vulnerability was found & reported by @crenshaw-dev (Michael Crenshaw)

The Argo team would like to thank these contributors for their responsible disclosure and constructive communications during the resolve of this issue

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-9m6p-x4h2-6frq
- https://nvd.nist.gov/vuln/detail/CVE-2024-32476
- https://github.com/argoproj/argo-cd/commit/7893979a1e78d59cedd0ba790ded24e30bb40657
- https://github.com/argoproj/argo-cd/commit/9e5cc5a26ff0920a01816231d59fdb5eae032b5a
- https://github.com/argoproj/argo-cd/commit/e2df7315fb7d96652186bf7435773a27be330cac
- https://github.com/argoproj/argo-cd
