# [C] Rancher Fleet vulnerable to cross namespace secret disclosure via unvalidated `valuesFrom` references in Helm Deployer

## Summary
Severity: Critical
Advisory: GHSA-xr65-5cpm-g36x
CVE: CVE-2026-44935
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-xr65-5cpm-g36x
Type: github-advisory

## Affected
- Go: `github.com/rancher/fleet` — affected >=0.15.0 <0.15.2
- Go: `github.com/rancher/fleet` — affected >=0.14.0 <0.14.6
- Go: `github.com/rancher/fleet` — affected >=0.13.0 <0.13.11
- Go: `github.com/rancher/fleet` — affected >=0.12.0 <0.12.15

## Details
### Impact
A vulnerability in Fleet for Rancher Manager affects multi-tenancy environments where different tenants share the same downstream clusters (e.g., different privileged or untrusted teams inside the same organization). 

On unpatched versions, tenants could bypass restrictions to access any config map or secret across all namespaces on the downstream cluster. They can create cluster-wide resources using `HelmOp` or `Bundle` without authorization.
Specifically, an attacker can exploit this vulnerability in the following ways:
1. Use `valuesFrom` in `fleet.yaml`(through a `GitRepo` resource) or a `HelmOp resource to read the contents of any secret an on the downstream cluster, provided they know or can guess the name, namespace, and key.
2. Deploy `HelmOp` and `Bundle` resources without being restricted to a specific service account for the Fleet agent.

If you use Fleet in a multi-tenant environment, it's recommended that you:
- Review your cluster and Fleet deployments logs for indicators of unauthorized access across tenant namespaces.
- Rotate any service accounts and credentials that might have been exposed.

Please consult the associated  [MITRE ATT&CK - Technique - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/) for further information about this category of attack.

### Patches
To resolve this vulnerability, upgrade to a patched version of Fleet.  The new Policy resource allows you to:
- Configure `GitRepos`, `HelmOps`, and `Bundles` to require a specific service account for the Fleet agent on downstream clusters used for deployment. The agent uses these designated service accounts for operations, blocking access to unauthorized resources.
- Restrict `HelmOp` repository and chart URLs by using a regular expression. The regular expression is automatically anchored with `^` and `$`, meaning it must match the entire URL string.

Like `GitRepoRestriction`, a Policy resource must be created in the specific namespace you want to restrict, and it only applies to that namespace.

**Note:** Before applying a policy, ensure that the required service account is available on the downstream clusters and is configured with least-privilege permissions.

Patched versions of Fleet include releases `v0.15.2`, `v0.14.6`, `0.13.11`, and `v0.12.15`.

### Workarounds
If you can't upgrade to a fixed version, please make sure that tenants do not have shared access to the same downstream clusters.

### Credits

This security issue was reported by the following collaborators according to our responsible disclosure policy:

- Radisauskas Arnoldas from NATO and the NATO Cyber Security Centre (NCSC).

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/fleet/security/advisories/GHSA-xr65-5cpm-g36x
- https://github.com/rancher/fleet
