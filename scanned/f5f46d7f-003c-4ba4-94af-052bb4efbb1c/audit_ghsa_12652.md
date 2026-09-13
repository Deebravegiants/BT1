# [C] Rancher vulnerable to Privilege Escalation via manipulation of Secrets

## Summary
Severity: Critical
Advisory: GHSA-p976-h52c-26p6
CVE: CVE-2023-22647
CWE: CWE-267, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-p976-h52c-26p6
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.13
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.4

## Details
### Impact

A vulnerability has been identified which enables [Standard users](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/global-permissions) or above to elevate their permissions to Administrator in the `local` cluster.

The `local` cluster means the cluster where Rancher is installed. It is named `local` inside the list of clusters in the Rancher UI.

Standard users could leverage their existing permissions to manipulate Kubernetes secrets in the `local` cluster, resulting in the secret being deleted, but their read-level permissions to the secret being preserved. When this operation was followed-up by other specially crafted commands, it could result in the user gaining access to tokens belonging to service accounts in the `local` cluster.

Users that have custom global roles which grant `create` and `delete` permissions on `secrets` would also be able to exploit this vulnerability.

Users with [audit logs enabled](https://ranchermanager.docs.rancher.com/how-to-guides/advanced-user-guides/enable-api-audit-log#enabling-api-audit-log) in Rancher can try to identify possible abuses of this issue by going through the logs. To sieve through the data filter by `kind: Secret` with `type: provisioning.cattle.io/cloud-credential`, then investigate all log entries that affect that specific resource. A secondary check would be to filter by all operations with `Opaque` Secrets within the `cattle-global-data` namespace.

After patching, it is recommended that users review access methods to Rancher (including RBAC policies, tokens, and host-level node access), to ensure that no changes were made to persist access to users who have leveraged this vulnerability.

### Patches

Patched versions include releases `2.6.13`, `2.7.4` and later versions. 

### Workarounds

There is no direct mitigation besides updating Rancher to a patched version.

### For more information

If you have any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-p976-h52c-26p6
- https://nvd.nist.gov/vuln/detail/CVE-2023-22647
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2023-22647
- https://github.com/rancher/rancher
- https://github.com/rancher/rancher/releases/tag/v2.6.13
- https://github.com/rancher/rancher/releases/tag/v2.7.4
