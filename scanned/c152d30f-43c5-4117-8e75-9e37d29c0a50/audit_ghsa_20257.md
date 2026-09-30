# [M] DoS through large manifest files in Argo CD

## Summary
Severity: Medium
Advisory: GHSA-jhqp-vf4w-rpwq
CVE: CVE-2022-31016
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-jhqp-vf4w-rpwq
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=0.7.0 <2.1.16
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.1.16
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.2.0 <2.2.10
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.3.0 <2.3.5
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.4.0 <2.4.1

## Details
### Impact

All versions of Argo CD starting with v0.7.0 are vulnerable to an uncontrolled memory consumption bug, allowing an authorized malicious user to crash the [repo-server](https://argo-cd.readthedocs.io/en/stable/operator-manual/architecture/#repository-server) service. The repo-server is a critical component of Argo CD, so crashing the repo-server effectively denies core Argo CD services (such as syncing Application updates).

To achieve denial of service, the attacker must be an authenticated Argo CD user authorized to deploy Applications from a repository which contains (or can be made to contain) a large file. 

### Patches

A patch for this vulnerability has been released in the following Argo CD versions:

* v2.4.1
* v2.3.5
* v2.2.10
* v2.1.16

**The patch introduces a new `reposerver.max.combined.directory.manifests.size` config parameter, which you should tune before upgrading in production.** It caps the maximum total file size of .yaml/.yml/.json files in directory-type (raw manifest) Applications. The default max is `10M` per Application. This max is designed to keep any single app from consuming more than 3G of memory in the repo-server (manifests consume more space in memory than on disk). The 300x ratio assumes a maliciously-crafted manifest file. If you only want to protect against accidental excessive memory use, it is probably safe to use a smaller ratio.

If your organization uses directory-type Applications with very many manifests or very large manifests then **check the size of those manifests and tune the config parameter before deploying this change to production**. When testing, make sure to do a "hard refresh" in either the CLI or UI to test your directory-type App. That will make sure you're using the new max logic instead of relying on cached manifest responses from Redis.

### Workarounds

There is no workaround besides upgrading.

To mitigate the issue, carefully limit 1) who can configure repos (determined by [RBAC](https://argo-cd.readthedocs.io/en/stable/getting_started/)), 2) which repos are allowed (determined by [Project](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/) limitations), and 3) who has push access to those repos (determined by your SCM provider configuration).

### Credits

Disclosed by ADA Logics in a security audit of the Argo project sponsored by CNCF and facilitated by OSTIF. Thanks to Adam Korczynski and David Korczynski for their work on the audit.

### For more information

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-jhqp-vf4w-rpwq
- https://nvd.nist.gov/vuln/detail/CVE-2022-31016
- https://github.com/argoproj/argo-cd
