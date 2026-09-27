# [H] Rancher's Steve API Component Improper authorization check allows privilege escalation

## Summary
Severity: High
Advisory: GHSA-gvh9-xgrq-r8hw
CVE: CVE-2021-36776
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-gvh9-xgrq-r8hw
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.10

## Details
### Impact

A flaw discovered in Rancher versions from 2.5.0 up to and including 2.5.9 allows an authenticated user to impersonate any user on a cluster through the Steve API proxy, without requiring knowledge of the impersonated user's credentials. This is due to the Steve API proxy not dropping the impersonation header before sending the request to the Kubernetes API. A malicious user with authenticated access to Rancher could use this to impersonate another user with administrator access in Rancher, receiving, then, administrator level access in the cluster.

### Patches
Patched versions include releases 2.5.10, 2.6.0 and later versions.

### Workarounds
Limit access in Rancher to trusted users. There is not a direct mitigation besides upgrading to the patched Rancher versions.

### For more information
If you have any questions or comments about this advisory:
* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36776
- https://bugzilla.suse.com/show_bug.cgi?id=1189413
- https://github.com/rancher/rancher
