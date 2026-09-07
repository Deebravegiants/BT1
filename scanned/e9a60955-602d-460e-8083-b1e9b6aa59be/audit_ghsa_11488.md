# [H] Rancher's Azure AD permission changes are not reflected on active sessions

## Summary
Severity: High
Advisory: GHSA-vf6j-6739-78m8
CVE: CVE-2023-22648
CWE: CWE-269, CWE-271, CWE-384
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-vf6j-6739-78m8
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.7 <2.6.13
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.4

## Details
A bug has been identified in which permission changes in Azure AD are not reflected to users while they are logged in the Rancher UI. This would cause the users to retain their previous permissions in Rancher, even if they change groups on Azure AD, for example, to a lower privileged group, or are removed from a group, thus retaining their access to Rancher instead of losing it.

### Impact
This issue only affects Rancher instances with Azure AD integration enabled, regardless of the [automatically refreshing settings](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/authentication-config/manage-users-and-groups#automatically-refreshing-user-information) which are enabled by default. The users that obtained a token (or kubeconfig) to access Rancher through the following sessions are affected by this issue:
1) Users using the Rancher UI.
2) Users using `kubectl` based on a `kubeconfig` downloaded through the Rancher UI.
3) Tokens created via the Rancher UI Create API Key feature.

Note that the permission caching is persisted even when the Rancher Manager pod is restarted. The only way for a user to get the new permissions is to logout and login again.

### Patches
Patched versions include releases `2.6.13`, `2.7.4` and later versions.

### For more information
If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-vf6j-6739-78m8
- https://nvd.nist.gov/vuln/detail/CVE-2023-22648
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-22648
- https://github.com/rancher/rancher
