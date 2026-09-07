# [C] Rancher has Privilege Escalation from Project Owner to Host

## Summary
Severity: Critical
Advisory: GHSA-vx8h-4prv-g744
CVE: CVE-2026-41052
CWE: CWE-305
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-vx8h-4prv-g744
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.14.0 <2.14.2
- Go: `github.com/rancher/rancher` — affected >=2.13.0 <2.13.6
- Go: `github.com/rancher/rancher` — affected >=2.12.0 <2.12.10
- Go: `github.com/rancher/rancher` — affected >=0 <0.0.0-20260513182521-2800aaac25b5

## Details
### Impact

A vulnerability has been identified in Rancher Manager that allows users assigned the Project Owner role to modify Pod Security Admission (PSA) labels on namespaces within their projects. Under the default role configuration, an attacker with the following access pattern can exploit this issue:
1. **Cluster Access:** The user is granted Cluster Member access.
2. **Project Ownership:** The user creates or is assigned ownership of a project.
3. **Namespace Creation:** The user creates a namespace within that project.
4. **PSA Modification:** The user modifies the namespace PSA configuration to use the privileged profile.
5. **Privilege Escalation:** The user deploys privileged workloads within the namespace.

As outlined in the [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) documentation, `privileged` containers disable core Kubernetes security protections, allowing workloads to bypass standard container isolation boundaries. This can result in privilege escalation within the cluster environment.

Potential impacts include:
- Deployment of privileged containers
- Access to host-level resources
- Container breakout
- Cluster privilege escalation
- Compromise of workloads running on affected nodes

Please refer to the associated MITRE ATT&CK techniques for further information about this category of attack:
- [Deploy Container](https://attack.mitre.org/techniques/T1610/)
- [Escape to Host](https://attack.mitre.org/techniques/T1611/)
- [Exploitation for Privilege Escalation](https://attack.mitre.org/techniques/T1068)

Reference:
[Kubernetes Pod Security Standards — Privileged Profile](https://kubernetes.io/docs/concepts/security/pod-security-standards/#privileged)

### Patches
This vulnerability is resolved by modifying the `project-owner` role to explicitly define the allowed verbs for `projects` resources instead of using the wildcard `(*)` permission.

The updated role configuration removes access to the `updatepsa` verb. This prevents project owners from modifying PSA settings in a manner that could enable privilege escalation.

Patched versions of Rancher include releases `v2.12.10`, `v2.13.6`, and `v2.14.2`.

### Workarounds
If upgrading is not immediately possible, administrators should create a custom project role based on the existing Project Owner role, while removing unrestricted wildcard permissions for project resources.

The allowed verbs for projects should be restricted to: “`get`, `update`, `delete`, `patch`, `create`, `list`, `watch`, `deletecollection`” instead of “`*`”.

This prevents access to the `updatepsa` capability that enables the privilege escalation path.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-vx8h-4prv-g744
- https://nvd.nist.gov/vuln/detail/CVE-2026-41052
- https://github.com/rancher/rancher/pull/55061
- https://github.com/rancher/rancher/commit/2800aaac25b5a2c448f800e1f46d
- https://github.com/rancher/rancher
