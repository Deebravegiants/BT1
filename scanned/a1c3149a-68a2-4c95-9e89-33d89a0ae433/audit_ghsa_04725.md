# [H] Omni: Reader-level users can retrieve imported cluster CA keys via ResourceService

## Summary
Severity: High
Advisory: GHSA-wv8c-6mx2-xf4j
CVE: CVE-2026-45726
CWE: CWE-200, CWE-522, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-wv8c-6mx2-xf4j
Type: github-advisory

## Affected
- Go: `github.com/siderolabs/omni` — affected >=1.3.0 <1.6.6
- Go: `github.com/siderolabs/omni` — affected >=1.7.0 <1.7.3

## Details
## Summary

Omni supports importing standalone Talos clusters.

During this process, an ImportedClusterSecrets resource is created, which contains the full CA secrets bundle for the cluster being imported.

If these secrets are not rotated by the importing actor, an authenticated Omni user with Reader access can read this resource and gain full access to the Talos, Kubernetes and etcd APIs of the cluster.

## Severity

- **Attack Vector:** Adjacent: the attacker needs to be in the same network to be able to access Talos/Kubernetes APIs with the compromised keys.
- **Attack Complexity:** High: the attacker needs a deep understanding of Omni's internals. The resource is only created for imported clusters, and is normally not represented to users via any high-level API.
- **Privileges Required:** Low: the role `Reader` is sufficient for the attacker to be able to read an imported cluster's secrets.
- **User Interaction:** Required: another user must have imported a cluster to Omni for this vulnerability to exist.
- **Scope:** Changed: the leaked CA private keys let an attacker directly get full control on Kubernetes or Talos, beyond the limitations enforced by Omni.
- **Confidentiality Impact:** High: full cluster CA private keys (Kubernetes, Talos, etcd, service account) are exposed.
- **Integrity Impact:** High: with the CA keys the attacker has full control on Kubernetes and Talos of the compromised (imported) cluster, and modify the workloads on it.
- **Availability Impact:** High: with the CA keys the attacker has full control on Kubernetes and Talos of the compromised (imported) cluster, and modify the workloads on it.

## Impact

- Any Reader-level account can exfiltrate the complete CA private key hierarchy (Kubernetes CA, etcd CA, service account key) of the imported clusters whose secrets are not yet rotated ("tainted" imported clusters).
- With the Kubernetes CA private key, an attacker can sign certificates for any Kubernetes user or group, including `system:masters`, achieving cluster-admin access to the imported cluster entirely outside Omni's control plane.
- Impact scope extends beyond Omni to every Kubernetes workload, credential, and secret stored in the affected imported cluster.

## Credit
This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/siderolabs/omni/security/advisories/GHSA-wv8c-6mx2-xf4j
- https://github.com/siderolabs/omni
- https://github.com/siderolabs/omni/releases/tag/v1.6.6
- https://github.com/siderolabs/omni/releases/tag/v1.7.3
