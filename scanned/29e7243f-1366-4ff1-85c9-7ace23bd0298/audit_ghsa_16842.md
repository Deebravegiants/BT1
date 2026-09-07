# [H] Rancher's Failure to delete orphaned role bindings does not revoke project level access from group based authentication

## Summary
Severity: High
Advisory: GHSA-28g7-896h-695v
CVE: CVE-2021-36775
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-28g7-896h-695v
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=0 <2.4.18
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.12
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.3

## Details
### Impact
This vulnerability only affects customers using group based authentication in Rancher versions up to and including 2.4.17, 2.5.11 and 2.6.2.

When removing a Project Role associated to a group from a project, the bindings that grant access to cluster scoped resources for those subjects do not get deleted. This happens due to an incomplete authorization logic check. A user who is a member of an affected group with authenticated access to Rancher could use this to access resources they should no longer have access to. The exposure level will depend on the original permission level granted to the affected project role.

### Patches
Patched versions include releases 2.4.18, 2.5.12, 2.6.3 and later versions.

### Workarounds
Limit access in Rancher to trusted users. There is not a direct mitigation besides upgrading to the patched Rancher versions.

### References
Cluster and project roles documentation for Rancher [2.6](https://rancher.com/docs/rancher/v2.6/en/admin-settings/rbac/cluster-project-roles/), [2.5](https://rancher.com/docs/rancher/v2.5/en/admin-settings/rbac/cluster-project-roles/) and [2.4](https://rancher.com/docs/rancher/v2.0-v2.4/en/admin-settings/rbac/cluster-project-roles/).

### For more information
If you have any questions or comments about this advisory:
* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-28g7-896h-695v
- https://nvd.nist.gov/vuln/detail/CVE-2021-36775
- https://bugzilla.suse.com/show_bug.cgi?id=1189120
- https://github.com/rancher/rancher
