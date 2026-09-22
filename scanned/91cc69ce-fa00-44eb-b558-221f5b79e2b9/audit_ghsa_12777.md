# [M] Denial of service (DoS) when processing Git credentials

## Summary
Severity: Medium
Advisory: GHSA-8fcj-gf77-47mg
CVE: CVE-2022-43756
CWE: CWE-150, CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2023-01-25
Source: https://github.com/advisories/GHSA-8fcj-gf77-47mg
Type: github-advisory

## Affected
- Go: `github.com/rancher/wrangler` — affected >=0 <0.7.4-security1
- Go: `github.com/rancher/wrangler` — affected >=0.8.0 <0.8.5-security1
- Go: `github.com/rancher/wrangler` — affected >=1.0.0 <1.0.1
- Go: `github.com/rancher/wrangler` — affected >=0.8.6 <0.8.11

## Details
### Impact

A denial of services (DoS) vulnerability was discovered in Wrangler Git package affecting versions up to and including `v1.0.0`.

Specially crafted Git credentials can result in a denial of service (DoS) attack on an application that uses Wrangler due to the exhaustion of the available memory and CPU resources. This is caused by a lack of input validation of Git credentials before they are used, which may lead to a denial of service in some cases. This issue can be triggered when accessing both private and public Git repositories. 

### Workarounds

A workaround is to sanitize input passed to the Git package to remove potential unsafe and ambiguous characters. Otherwise, the best course of action is to update to a patched Wrangler version.

### Patches

Patched versions include `v1.0.1` and later and the backported tags - `v0.7.4-security1`, `v0.8.5-security1` and `v0.8.11`.

### For more information

If you have any questions or comments about this advisory:

* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) or [Wrangler](https://github.com/rancher/wrangler/issues/new) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/wrangler/security/advisories/GHSA-8fcj-gf77-47mg
- https://nvd.nist.gov/vuln/detail/CVE-2022-43756
- https://github.com/rancher/wrangler/commit/341018c8fef3e12867c7cb2649bd2cecac75f287
- https://bugzilla.suse.com/show_bug.cgi?id=1205296
- https://github.com/advisories/GHSA-8fcj-gf77-47mg
- https://github.com/rancher/rancher/security/policy
- https://github.com/rancher/wrangler
- https://pkg.go.dev/vuln/GO-2023-1515
