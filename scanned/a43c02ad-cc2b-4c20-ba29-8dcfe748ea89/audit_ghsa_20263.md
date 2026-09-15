# [M] Symlink following allows leaking out-of-bounds YAML files from Argo CD repo-server

## Summary
Severity: Medium
Advisory: GHSA-q4w5-4gq2-98vm
CVE: CVE-2022-31036
CWE: CWE-20, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-q4w5-4gq2-98vm
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=1.3.0 <2.1.16
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.1.16
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.2.0 <2.2.10
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.3.0 <2.3.5
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.4.0 <2.4.1

## Details
### Impact

All unpatched versions of Argo CD starting with v1.3.0 are vulnerable to a symlink following bug allowing a malicious user with repository write access to leak sensitive YAML files from Argo CD's repo-server.

A malicious Argo CD user with write access for a repository which is (or may be) used in a Helm-type Application may commit a symlink which points to an out-of-bounds file. If the target file is a valid YAML file, the attacker can read the contents of that file.

Sensitive files which could be leaked include manifest files from other Applications' source repositories (potentially decrypted files, if you are using a decryption plugin) or any YAML-formatted secrets which have been mounted as files on the repo-server.

### Patches

A patch for this vulnerability has been released in the following Argo CD versions:

* v2.4.1
* v2.3.5
* v2.2.10
* v2.1.16

### Workarounds

* If you are using >=v2.3.0 and do not have any Helm-type Applications, [disable the Helm config management tool](https://argo-cd.readthedocs.io/en/stable/user-guide/tool_detection/#disable-built-in-tools).

#### Mitigations

* Avoid mounting YAML-formatted secrets as files on the repo-server.
* Upgrade to >=2.3.0 to significantly reduce the risk of leaking out-of-bounds manifest files. Starting with 2.3.0, repository paths are randomized, and read permissions are restricted when manifests are not being actively being generated. This makes it very difficult to craft and use a malicious symlink.

#### Best practices which can mitigate risk

* Limit who has push access to manifest repositories.
* Limit who is allowed to configure new source repositories.

### Credits

Disclosed by ADA Logics in a security audit of the Argo project sponsored by CNCF and facilitated by OSTIF. Thanks to Adam Korczynski and David Korczynski for their work on the audit.

### References

* List of [types of Applications](https://argo-cd.readthedocs.io/en/stable/user-guide/application_sources/), including Helm-type
* [RBAC documentation](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/), showing how to limit repository permissions

### For more information

* Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
* Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-q4w5-4gq2-98vm
- https://nvd.nist.gov/vuln/detail/CVE-2022-31036
- https://github.com/argoproj/argo-cd/commit/04c305396458508a31d03d44afea07b1c620d7cd
- https://github.com/argoproj/argo-cd
