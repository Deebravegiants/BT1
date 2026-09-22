# [H] Rancher permissions on 'namespaces' in any API group grants 'edit' permissions on namespaces in 'core'

## Summary
Severity: High
Advisory: GHSA-c85r-fwc7-45vc
CVE: CVE-2023-32194
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-c85r-fwc7-45vc
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.14
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.10
- Go: `github.com/rancher/rancher` — affected >=2.8.0 <2.8.2

## Details
### Impact
A vulnerability has been identified when granting a `create` or `*` **global role** for a resource type of "namespaces"; no matter the API group, the subject will receive `*` permissions for core namespaces. This can lead to someone being capable of accessing, creating, updating, or deleting a namespace in the project. This includes reading or updating a namespace in the project so that it is available in other projects in which the user has the "manage-namespaces" permission or updating another namespace in which the user has normal "update" permissions to be moved into the project.

The expected behavior is to not be able to create, update, or delete a namespace in the project or move another namespace into the project since the user doesn't have any permissions on namespaces in the core API group.

Moving a namespace to another project could lead to leakage of secrets, in case the targeted project has secrets. And also can lead to the namespace being able to abuse the resource quotas of the targeted project.

### Patches
Patched versions include releases `2.6.14`, `2.7.10` and `2.8.2`.

### Workarounds
There is no direct mitigation besides updating Rancher to a patched version.

### References
If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security-related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-c85r-fwc7-45vc
- https://nvd.nist.gov/vuln/detail/CVE-2023-32194
- https://github.com/rancher/rancher/commit/2f7113dc32d4f1f5375a1ae09b65be58f6801a15
- https://github.com/rancher/rancher/commit/649fdad268d8ecc748e9fdcca2ddcfdc900f9eaa
- https://github.com/rancher/rancher/commit/d4a0ff5e779e3cc5f14d77ce57620e1326ab1c22
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-32194
- https://github.com/rancher/rancher
