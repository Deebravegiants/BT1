# [M] Privilege escalation for users with create/update permissions in Global Roles in Rancher

## Summary
Severity: Medium
Advisory: GHSA-jwvr-vv7p-gpwq
CVE: CVE-2021-36784
CWE: CWE-269, CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-jwvr-vv7p-gpwq
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.4
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.13

## Details
### Impact
This vulnerability affects customers who utilize non-admin users that are able to create or edit [Global Roles](https://rancher.com/docs/rancher/v2.6/en/admin-settings/rbac/). The most common use case for this scenario is the [`restricted-admin`](https://rancher.com/docs/rancher/v2.6/en/admin-settings/rbac/global-permissions/#restricted-admin) role.

A flaw was discovered in Rancher versions from 2.5.0 up to and including 2.5.12 and from 2.6.0 up to and including 2.6.3 which allows users who have create or update permissions on Global Roles to escalate their permissions, or those of another user, to admin-level permissions. Global Roles grant users Rancher-wide permissions, such as the ability to create clusters. In the identified versions of Rancher, when users are given permission to edit or create Global Roles, they are not restricted to only granting permissions which they already posses.

The privilege escalation can be taken advantage of in two ways by users with create or update permissions on Global Roles (including the `restricted-admin`):

1. Editing the global `admin` role to make it the default for new users, then creating a new user that will be elevated to the global `admin` role.
2. Creating a new global role with permissions already possessed by the `restricted-admin`, assigning this new role to a user, then modifying the global role to grant additional administrive like permissions (`'*'`) to the elevated user.

### Patches
Patched versions include releases 2.5.13, 2.6.4 and later versions.

### Workarounds
Limit access in Rancher to trusted users. There is not a direct mitigation besides upgrading to the patched Rancher versions.

**Note:** If you have users who have create or edit permissions on Global Roles but are not admin users (for example, the `restricted-admin`), it is highly advised to review the roles and users created by those users for possible privilege escalations.

### For more information
If you have any questions or comments about this advisory:
* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-jwvr-vv7p-gpwq
- https://nvd.nist.gov/vuln/detail/CVE-2021-36784
- https://bugzilla.suse.com/show_bug.cgi?id=1193991
- https://github.com/rancher/rancher/releases/tag/v2.5.13
- https://github.com/rancher/rancher/releases/tag/v2.6.4
- github.com/rancher/rancher
