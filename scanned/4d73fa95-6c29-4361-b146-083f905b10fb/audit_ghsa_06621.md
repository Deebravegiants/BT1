# [C] Rancher vulnerable to command injection through unsanitized YAML parameter

## Summary
Severity: Critical
Advisory: GHSA-mhc6-2gfq-xx62
CVE: CVE-2026-44939
CWE: CWE-95
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-mhc6-2gfq-xx62
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.14.0 <2.14.2
- Go: `github.com/rancher/rancher` — affected >=2.13.0 <2.13.6
- Go: `github.com/rancher/rancher` — affected >=2.12.0 <2.12.10
- Go: `github.com/rancher/rancher` — affected >=2.11.0 <2.11.14
- Go: `github.com/rancher/rancher` — affected >=2.10.0 <2.10.12
- Go: `github.com/rancher/rancher` — affected >=0 <0.0.0-20260617231817-2aa77eb283e7

## Details
### Impact
A critical command injection vulnerability has been identified in the Rancher Manager cluster import endpoint  `/v3/import/{token}_{clusterId}.yaml` through unsanitized YAML parameters. This endpoint accepts an `authImage` query parameter that is rendered without sanitization into a generated Kubernetes manifest template. By including URL-encoded newlines in the parameter value, an attacker can break out of the `image:` field to inject arbitrary YAML keys and malicious configurations, such as commands to execute malicious containers.

Exploitation of this vulnerability requires the following conditions to be met:
- Attackers must obtain a valid cluster registration token (these tokens may be exposed, for example, through documentation, screenshots, or insecure communication channels).
- The victim’s cluster operator must execute `kubectl apply` against a maliciously crafted URL. 

When a victim applies this compromised manifest using `kubectl apply`, a DaemonSet is deployed with the injected configuration. This DaemonSet:
- Runs on all control-plane nodes with `hostNetwork: true` enabled.
- Uses the `cattle` service account, which possesses `cluster-admin` privileges.
- Mounts `/etc/kubernetes` directly from the host.
- Executes attacker-controlled commands via the injected `command:` field.

An attacker who successfully exploits this vulnerability could:

- Achieve full control over downstream Kubernetes clusters.
- Execute arbitrary code on control-plane nodes with elevated privileges.
- Access sensitive cluster secrets and configurations via the privileged service account.
- Disrupt cluster operations by manipulating critical control-plane workloads.
- Establish persistent access through the deployed DaemonSet.

**Note:** If you believe that you might have been impacted by this vulnerability, it's highly advised to review your clusters' logs and deployment logs for signs of malicious deployments and to rotate all service accounts and credentials that might have been exposed in such a scenario.

Please refer to the associated  [MITRE ATT&CK - Technique - Deploy Container](https://attack.mitre.org/techniques/T1610/) for further information about this category of attack.

### Patches
This vulnerability is addressed by validating the `authImage` parameter to ensure it contains only valid OCI image reference characters, rejecting any input containing newlines, whitespace, or other characters that could break YAML syntax.

Patched versions of Rancher include release `v2.14.2`, `v2.13.6`, `v2.12.10`, `v2.11.14` and `v2.10.12`. 

### Workarounds
If upgrading to a patched version immediately is not feasible, users are encouraged to apply the following workaround: 

- Review the `kube-api-auth` DaemonSet: Inspect downstream clusters for the `kube-api-auth` DaemonSet within the `cattle-system` namespace (which targets control-plane nodes). Review this resource configuration carefully for:
  - Unexpected `command:` or `args:` fields in the container specification.
  - References to non-standard or suspicious container images.
  - Any modifications occurring after the initial cluster import.
- Validate manifest integrity: Before running `kubectl apply` on any import manifests, verify that the source URLs originate from trusted sources and match expected patterns.

### Credits

This security issue was reported by the following collaborators according to our responsible disclosure policy:

- Radisauskas Arnoldas from NATO and the NATO Cyber Security Centre (NCSC).
- Michael Wollner from Deutsche Telekom AG.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-mhc6-2gfq-xx62
- https://nvd.nist.gov/vuln/detail/CVE-2026-44939
- https://github.com/rancher/rancher/commit/2aa77eb283e7451d605fb85e1bd9b1791cd73875
- https://github.com/rancher/rancher
