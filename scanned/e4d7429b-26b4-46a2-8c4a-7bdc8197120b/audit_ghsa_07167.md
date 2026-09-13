# [M] Rancher Fleet has SSRF in Bundle Reader via Unvalidated Helm Repository URL in fleet.yaml

## Summary
Severity: Medium
Advisory: GHSA-hx4v-cxpf-vh8m
CVE: CVE-2026-44936
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-hx4v-cxpf-vh8m
Type: github-advisory

## Affected
- Go: `github.com/rancher/fleet` — affected >=0.15.0 <0.15.2
- Go: `github.com/rancher/fleet` — affected >=0.14.0 <0.14.6
- Go: `github.com/rancher/fleet` — affected >=0.13.0 <0.13.11
- Go: `github.com/rancher/fleet` — affected >=0.12.0 <0.12.15

## Details
### Impact
A vulnerability has been identified in Fleet when the `helmRepoURLRegex` field isn't set on a `GitRepo` resource. Fleet's bundle reader forwards Helm authentication credentials (`BasicAuth`) to any URL specified in the `helm.repo` field of a `fleet.yaml` file.

An attacker with git push access to a Fleet-monitored repository can exploit this behavior by specifying a malicious URL in `helm.repo`. This causes the Fleet controller to send the configured Helm repository credentials to the attacker’s server. 

As a result, the attacker can capture the username and password that an administrator configured to access a private Helm chart repository. However, the response body from the attacker's server isn't included in the error message (this behavior was fixed in Fleet `v0.13.3` and later), which prevents additional internal data from leaking through the status condition.

The final severity of this vulnerability depends on the specific permissions of the leaked credentials. 

Fleet recommends you to:
1. Review your system for potentially leaked credentials.
2. Replace any credentials that might be compromised.

Please consult the associated [MITRE ATT&CK - Technique - Stored Data Manipulation](https://attack.mitre.org/techniques/T1565/001/) and [MITRE ATT&CK - Technique - Steal Application Access Token](https://attack.mitre.org/techniques/T1528/) for further information about this category of attack.

### Patches
To resolve this vulnerability, upgrade to a patched version of Fleet. The patched version of Fleet now requires you to set the `helmRepoURLRegex` field on the `GitRepo`. If the `helmRepoURLRegex` is empty or missing, Fleet won’t send credentials, regardless of the URL specified in `fleet.yaml`.
 
When you upgrade, a Helm pre-upgrade job automatically migrates existing `GitRepo` resources that have `helmSecretName` or `helmSecretNameForPaths` configured but lack a `helmRepoURLRegex`. The migration job performs the following actions:

The job extracts the scheme and host from the Helm repository URLs already stored in the resource's Bundles. For example, a `GitRepo` with Bundles referencing `https://charts.example.com/stable` receives `helmRepoURLRegex: "^https://charts\.example\.com/"`. This limits credential forwarding to the origins already in use before the upgrade.
Migrated resources are annotated with `fleet.cattle.io/helm-regex-auto-migrated: "true"` so you can easily audit them.

If no Bundles with Helm repository URLs exist during the migration (for example, if the `GitRepo` has never successfully synced), `helmRepoURLRegex` remains empty and credentials aren't forwarded. You must set this field manually before Fleet will send credentials.

The migration job runs only once per installation and records its status in a `ConfigMap` named `fleet-helm-url-regex-migrated` in the Fleet system namespace. Any `GitRepo` resources you create after the upgrade require an explicit `helmRepoURLRegex` to forward credentials.

Patched versions of Fleet include releases `v0.15.2`, `v0.14.6`, `0.13.11`, and `v0.12.15`.

### Workarounds
If you cannot immediately upgrade to a patched version, use the following methods to mitigate the risk and audit your environment.
Set `helmRepoURLRegex` on all `GitRepo` resources that use `helmSecretName`. Ensure the regular expression matches only your legitimate Helm repository URL. 

Example configuration:
```yaml
apiVersion: fleet.cattle.io/v1alpha1
kind: GitRepo
metadata:
  name: my-app
  namespace: fleet-local
spec:
  repo: https://git.example.com/org/my-app.git
  helmSecretName: helm-creds
  helmRepoURLRegex: "^https://charts\\.example\\.com/.*"
```

After upgrading to a patched version, review all auto-migrated `GitRepo` resources by running the following command:

``` 
kubectl get gitrepo -A -o json | \
  jq -r '.items[] | select(.metadata.annotations["fleet.cattle.io/helm-regex-auto-migrated"] == "true") | "\(.metadata.namespace)/\(.metadata.name): \(.spec.helmRepoURLRegex)"'
```

Verify that the auto-derived regular expression matches only your intended Helm repository origins. If a regular expression is broader than necessary, replace it with a more specific pattern.

### Credits

This security issue was reported by the following collaborators according to our responsible disclosure policy:

- Radisauskas Arnoldas from NATO and the NATO Cyber Security Centre (NCSC).
- FluentLogic's security team.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/fleet/security/advisories/GHSA-hx4v-cxpf-vh8m
- https://github.com/rancher/fleet
