# [H] Rancher Fleet Helm Values are stored inside BundleDeployment in plain text

## Summary
Severity: High
Advisory: GHSA-6h9x-9j5v-7w9h
CVE: CVE-2024-52284
CWE: CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-6h9x-9j5v-7w9h
Type: github-advisory

## Affected
- Go: `github.com/rancher/fleet` — affected >=0.13.0 <0.13.1-0.20250806151509-088bcbea7edb
- Go: `github.com/rancher/fleet` — affected >=0.12.0 <0.12.6
- Go: `github.com/rancher/fleet` — affected >=0.11.0 <0.11.10

## Details
### Impact
A vulnerability has been identified when using Fleet to manage Helm charts where sensitive information is passed through `BundleDeployment.Spec.Options.Helm.Values` may be stored in plain text. This can result in: 
1. Unauthorized disclosure of sensitive data: Any user with `GET` or `LIST` permissions on `BundleDeployment` resources could retrieve Helm values containing credentials or other secrets.
2. Lack of encryption at rest: `BundleDeployment` is not configured for Kubernetes encryption at rest by default, causing sensitive values to remain unencrypted within the cluster datastore.

This behavior differs from Helm v3’s default approach, where chart state — including values — is stored in Kubernetes secrets, benefiting from built-in protection mechanisms. In affected scenarios, credentials and other sensitive information are exposed both at rest and in responses to API calls.

Please consult the associated  [MITRE ATT&CK - Technique - Credentials from Password Stores](https://attack.mitre.org/techniques/T1555/) for further information about this category of attack.

For the exposure of credentials not related to Rancher, the final impact severity for confidentiality, integrity, and availability is dependent on the permissions that the leaked credentials have on their own services.
It is recommended to review the potentially exposed sensitive data in this scenario and change secrets, tokens, and passwords as necessary.

### Patches
This vulnerability is addressed by adding the capability for each `Bundle` and `BundleDeployment` to have a secret to store options in.
1. The git job that runs `fleet apply` will now create secrets for Helm values.
2. Fleet controller generates `bundledeployments` and now creates a Helm values secret per bundle deployment in the cluster namespace.
3. Fleet agent uses the `bundledeployment` for options, the content resource and the secret to deploy the bundle.


Patched versions of Fleet include releases `v0.14.0`, `v0.13.1`, `v0.12.6` and `v0.11.10`.

### Workarounds
If you can't upgrade to a fixed version, please make sure to specify paths to valuesFiles as simple file names, e.g.:

Instead of:
```fleet.yaml
helm:
  valuesFiles:
    - config-chart/values.yaml # will not be excluded → risky
```
Use:
```fleet.yaml
helm:
  valuesFiles:
    - values.yaml # will be excluded
```

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/fleet/security/advisories/GHSA-6h9x-9j5v-7w9h
- https://github.com/rancher/fleet/commit/088bcbea7edb844d7e6fc3649d9954f763cf68a9
- https://github.com/rancher/fleet
