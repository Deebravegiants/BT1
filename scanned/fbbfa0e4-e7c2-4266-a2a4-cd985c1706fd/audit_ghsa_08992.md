# [C] Fleet: Helm impersonation bypass of `RESTClientGetter` retains `cluster-admin` during template rendering

## Summary
Severity: Critical
Advisory: GHSA-765j-qfrp-hm3j
CVE: CVE-2026-41050
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-765j-qfrp-hm3j
Type: github-advisory

## Affected
- Go: `github.com/rancher/fleet` — affected >=0.15.0 <0.15.1
- Go: `github.com/rancher/fleet` — affected >=0.14.0 <0.14.5
- Go: `github.com/rancher/fleet` — affected >=0.13.0 <0.13.10
- Go: `github.com/rancher/fleet` — affected >=0.12.0 <0.12.14
- Go: `github.com/rancher/fleet` — affected >=0.11.0 <0.11.13

## Details
### Impact

Fleet's Helm deployer did not fully apply ServiceAccount impersonation in two code paths, allowing a tenant with git push access to a Fleet-monitored repository to read secrets from any namespace on every downstream cluster targeted by their `GitRepo`.

**Helm `lookup` bypass:** The Helm template engine ran Kubernetes API queries with the fleet-agent's cluster-admin credentials instead of the impersonated ServiceAccount. A chart template could therefore access resources beyond the tenant's RBAC scope.

**`valuesFrom` bypass:** Secret and ConfigMap references in `fleet.yaml` `helm.valuesFrom` were read using the fleet-agent's cluster-admin client. A tenant could reference resources in namespaces the impersonated ServiceAccount has no access to.
Both issues break Fleet's multi-tenant impersonation boundary. The leaked credentials may belong to external services, making the full impact non-deterministic.
Single-tenant deployments where all users are trusted are not affected.

**Important:**
- For the exposure of additional credentials, the final impact severity for confidentiality, integrity and availability is dependent on the permissions the leaked credentials have on their services.
- It is recommended to review for potentially leaked credentials in this scenario and to change them if deemed necessary.

Please consult the associated  [MITRE ATT&CK - Technique - Account Access Removal](https://attack.mitre.org/techniques/T1531/) for further information about this category of attack.

### Patches

Both issues are fixed by ensuring the Helm action configuration consistently uses the impersonated ServiceAccount credentials throughout all Helm operations.

Patched versions of Rancher include releases `v2.14.1`, `v2.13.5`, `v2.12.9`, and `v2.11.13`. For Rancher `v2.10.11`, users must manually update their Fleet deployment to version`v0.11.13`.

### Workarounds

No workaround fully mitigates the issue for multi-tenant deployments. The patches should be applied as soon as they are available.

The following measures reduce the attack surface but do not close either vulnerability:

- Restrict git push access to Fleet-monitored repositories to trusted users only. In a multi-tenant setup this removes the precondition entirely, but is often not operationally viable.
- Use `GitRepoRestriction` resources to limit which ServiceAccounts each namespace is allowed to use, restricting the set of users who can configure impersonation at all.
- Audit deployed chart templates for `lookup` calls and `fleet.yaml` files for cross-namespace `valuesFrom` references as a detective control.

### Resources

If there are any questions or comments about this advisory:

- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify using the [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/fleet/security/advisories/GHSA-765j-qfrp-hm3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-41050
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-41050
- https://github.com/rancher/fleet
