# [M] Symlink following allows leaking out-of-bound manifests and JSON files from Argo CD repo-server

## Summary
Severity: Medium
Advisory: GHSA-6gcg-hp2x-q54h
CVE: CVE-2022-24904
CWE: CWE-59, CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-23
Source: https://github.com/advisories/GHSA-6gcg-hp2x-q54h
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0 <2.1.15
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.2.0 <2.2.9
- Go: `github.com/argoproj/argo-cd/v2` — affected >=2.3.0 <2.3.4

## Details
### Impact

All unpatched versions of Argo CD starting with v0.7.0 are vulnerable to a symlink following bug allowing a malicious user with repository write access to leak sensitive files from Argo CD's repo-server.

A malicious Argo CD user with write access for a repository which is (or may be) used in a directory-type Application may commit a symlink which points to an out-of-bounds file. 
* If the target file is a valid JSON or YAML manifest file, and the resource is allowed in the Application, the attacker can read the contents of that manifest file. (In versions <2.3.2, <2.2.8, and <2.1.14, the attacker may read the files contents even if the resource is _not_ allowed in the Application). 
* If the target file is valid JSON but is _not_ a manifest file, the attacker may read the contents of the file. 
* If the target file is not valid JSON or YAML, the attacker may read partial file contents (usually just the first character of the file).

Sensitive files which could be leaked include manifest files from other Applications' source repositories (potentially decrypted files, if you are using a decryption plugin) or any JSON-formatted secrets which have been mounted as files on the repo-server.

### Patches

A patch for this vulnerability has been released in the following Argo CD versions:

* v2.3.4
* v2.2.9
* v2.1.15

### Workarounds

* If you are using >=v2.3.0 and do not have any Jsonnet/directory-type Applications, [disable the Jsonnet/directory config management tool](https://argo-cd.readthedocs.io/en/stable/user-guide/tool_detection/#disable-built-in-tools). The config key is called `jsonnet.enable` since the same build tool is used for both Jsonnet and plain-manifest ("directory") sources.

#### Mitigations

* Avoid mounting JSON-formatted secrets as files on the repo-server.
* Upgrade to >=2.3.0 to significantly reduce the risk of leaking out-of-bounds manifest files. Starting with 2.3.0, repository paths are randomized, and read permissions are restricted when manifests are not being actively being generated. This makes it very difficult to craft and use a malicious symlink.
* Upgrade to >=2.3.3, >=2.2.8, or >= 2.1.14 to significantly reduce the risk of leaking the contents of (but not the existence of) out-of-bounds manifest files. These versions prevent attackers from loading manifests which are not permitted in the Project which governs the Application. 

#### Best practices which can mitigate risk

* Limit who has push access to manifest repositories.
* Limit who is allowed to configure new source repositories.
* Limit resource kinds and destinations allowed for Projects, and restrict user access to only the necessary Projects.

### Credits

This vulnerability was originally discovered as part of the Trail of Bits audit, published March 12, 2021. The behavior was left unchanged at the time.

The vulnerability was independently re-discovered by @crenshaw-dev, who contributed the patch. A security audit by Ada Logics independently followed up on the Trail of Bits report around the same time.

### References

* List of [types of Applications](https://argo-cd.readthedocs.io/en/stable/user-guide/application_sources/), including directory-type
* [RBAC documentation](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/), showing how to limit repository permissions
* [Project documentation](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/), showing how to limit allowable resource kinds and destinations 

### For more information
Open an issue in [the Argo CD issue tracker](https://github.com/argoproj/argo-cd/issues) or [discussions](https://github.com/argoproj/argo-cd/discussions)
Join us on [Slack](https://argoproj.github.io/community/join-slack) in channel #argo-cd

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-6gcg-hp2x-q54h
- https://nvd.nist.gov/vuln/detail/CVE-2022-24904
- https://github.com/argoproj/argo-cd/commit/5e767a4b9e30983330c0fdec322192281a90eb84
- https://github.com/argoproj/argo-cd/commit/7357cfdb58a560de70a0538c6e3bef6fe39505ea
- https://github.com/argoproj/argo-cd/commit/d36d95dc9f71ec61c1a93794f81ece6d61a0d943
- https://github.com/argoproj/argo-cd/releases/tag/v2.1.15
- https://github.com/argoproj/argo-cd/releases/tag/v2.2.9
- https://github.com/argoproj/argo-cd/releases/tag/v2.3.4
- github.com/argoproj/argo-cd
