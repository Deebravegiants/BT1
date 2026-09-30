# [M] Rancher Helm Applications may have sensitive values leaked

## Summary
Severity: Medium
Advisory: GHSA-9c5p-35gj-jqp4
CVE: CVE-2024-52282
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-20
Source: https://github.com/advisories/GHSA-9c5p-35gj-jqp4
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.8.0 <2.8.10
- Go: `github.com/rancher/rancher` — affected >=2.9.0 <2.9.4

## Details
### Impact
A vulnerability has been identified within Rancher Manager whereby applications installed via Rancher Manager Apps Catalog store their Helm values directly into the `Apps` Custom Resource Definition, resulting in any users with `GET` access to it to be able to read any sensitive information that are contained within the Apps’ values. Additionally, the same information leaks into auditing logs when the audit level is set to equal or above 2.

Application charts without sensitive data are not affected by this vulnerability.
This vulnerability impacts any Helm applications installed on a Rancher Manager cluster, regardless of it being installed via the Marketplace or using the helm cli.

Please consult the associated [MITRE ATT&CK - Technique - Exploitation for Privilege Escalation](https://attack.mitre.org/techniques/T1068/) for further information about this category of attack.

### Patches
Patched versions include Rancher Manager `2.9.5` and `2.8.10`. The fix ensures that all Helm values for each App are stored as Kubernetes Secrets. After the upgrade, users are recommended to rotate passwords and secrets that may have been leaked while using the affected versions.

### Workarounds
No workarounds are available, therefore users are advised to upgrade to a patched version of Rancher Manager.
For deployments that can’t be upgraded in a timely fashion, admins are advised to limit the impact by reducing the amount of users who can get or list the Apps’ CRD. Additionally, the same applies to the auditing logs if the Rancher Manager has audit logs enabled and set to level 2 or above.

### For more information
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-9c5p-35gj-jqp4
- https://nvd.nist.gov/vuln/detail/CVE-2024-52282
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2024-52282
- https://github.com/rancher/rancher
- https://pkg.go.dev/vuln/GO-2024-3280
