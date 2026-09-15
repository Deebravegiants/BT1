# [H] Fleet has PSS Bypass through addLabelsFromOptions in Fleet Agent

## Summary
Severity: High
Advisory: GHSA-864g-863m-vcvq
CVE: CVE-2026-44938
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-864g-863m-vcvq
Type: github-advisory

## Affected
- Go: `github.com/rancher/fleet` — affected >=0.15.0 <0.15.2
- Go: `github.com/rancher/fleet` — affected >=0.14.0 <0.14.6
- Go: `github.com/rancher/fleet` — affected >=0.13.0 <0.13.11
- Go: `github.com/rancher/fleet` — affected >=0.12.0 <0.12.15

## Details
### Impact
A vulnerability has been identified in Fleet's agent-side deployer, which did not filter security-sensitive keys from `namespaceLabels` in `fleet.yaml` (or `BundleDeployment.spec.options.namespaceLabels`) when applying them to the target namespace. 

An attacker with `git push` access to a Fleet-monitored repository could overwrite Pod Security Standards (PSS) enforcement labels on a target namespace. This allows the attacker to weaken admission controls and deploy workloads that PSS policies would otherwise block.

**Important:** The final impact on confidentiality, integrity, and availability depends on the specific permissions of the leaked credentials. 

Fleet team recommends you:
1. Review your system for potentially leaked credentials.
2. Replace any credentials that may be compromised.

Please consult the associated  [MITRE ATT&CK - Technique - Disable or Modify Tools](https://attack.mitre.org/techniques/T1685/) for further information about this category of attack.

### Patches
To fix this issue, upgrade to a patched version. The updated Fleet deployer filters out labels with the `pod-security.kubernetes.io/` prefix when applying `namespaceLabels` to a namespace. This change preserves the PSS labels set by cluster administrators and prevents them from being overwritten through `fleet.yaml` or `BundleDeployment` options.

Patched versions of Fleet include releases `v0.15.2`, `v0.14.6`, `v0.13.11`, and `v0.12.15`.

### Workarounds
If you can’t immediately upgrade to a patched version, use one of the following workarounds:

**1 - Deploy NeuVector(primary workaround)**

Deploy NeuVector (SUSE Security) and configure an admission control Deny rule for "Run as privileged" in Protect mode. 
- NeuVector evaluates pod specs independently of Kubernetes PSS namespace labels. It blocks privileged containers even if the labels are downgraded. 
- Although the namespace labels are still overwritten, the attack cannot exploit confidentiality, integrity, or availability without a privileged pod.

**2 - Restrict repository access (secondary workaround)**

**Note:** The following measure reduces the attack surface but does not close the vulnerability:
- In a multi-tenant setup, this restriction removes the primary attack vector. However, this measure only reduces the attack surface and doesn't completely close the vulnerability. It may also not be operationally viable for all organizations. ´

### Credits

This security issue was reported by the following collaborators according to our responsible disclosure policy:

- Radisauskas Arnoldas from NATO and the NATO Cyber Security Centre (NCSC).

### References
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/fleet/security/advisories/GHSA-864g-863m-vcvq
- https://github.com/rancher/fleet
