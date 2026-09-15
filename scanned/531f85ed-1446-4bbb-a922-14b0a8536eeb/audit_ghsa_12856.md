# [M] Command injection in Rancher Git package

## Summary
Severity: Medium
Advisory: GHSA-34p5-jp77-fcrc
CVE: CVE-2022-43758
CWE: CWE-77, CWE-78, CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-25
Source: https://github.com/advisories/GHSA-34p5-jp77-fcrc
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.17
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.10
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.1

## Details
### Impact

An issue was discovered in Rancher from versions 2.5.0 up to and including 2.5.16, 2.6.0 up to and including 2.6.9 and 2.7.0, where a command injection vulnerability is present in the Rancher Git package. This package uses the underlying Git binary available in the Rancher container image to execute Git operations.

Specially crafted commands, when not properly disambiguated, can cause confusion when executed through Git, resulting in command injection in the underlying Rancher host.

This issue can potentially be exploited in Rancher in two ways:

1. Adding an untrusted Helm catalog, in the Catalogs menu, that contains maliciously designed repo URL configuration in Helm charts.
2. Modifying the URL configuration used to download KDM (Kontainer Driver Metadata) releases.

By default, only the Rancher admin has permission to manage both configurations for the local cluster (the cluster where Rancher is provisioned).

Note: More information about this category of issue in version control system (VCS) tools are available in Snyk's [blog post](https://snyk.io/blog/argument-injection-when-using-git-and-mercurial/).

### Workarounds

Except for only adding trusted catalogs and the KDM URL to Rancher, there is no other workaround besides updating Rancher to a patched version.

### Patches

Patched versions include releases 2.5.17, 2.6.10, 2.7.1 and later versions.

It is also important to update to a patched version in case Rancher or its standalone Git package implementation is used as a Go library instead of the application itself. Otherwise, this vulnerability might affect your dependent code.

### For more information

If you have any questions or comments about this advisory:

* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-34p5-jp77-fcrc
- https://nvd.nist.gov/vuln/detail/CVE-2022-43758
- https://bugzilla.suse.com/show_bug.cgi?id=1205294
- https://github.com/rancher/rancher
