# [H] Plaintext storage of sensitive data in Rancher API and cluster.management.cattle.io objects

## Summary
Severity: High
Advisory: GHSA-cq4p-vp5q-4522
CVE: CVE-2022-43757
CWE: CWE-200, CWE-256, CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-25
Source: https://github.com/advisories/GHSA-cq4p-vp5q-4522
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.17
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.10
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.1

## Details
### Impact

This issue affects Rancher versions from 2.5.0 up to and including 2.5.16, from 2.6.0 up to and including 2.6.9 and 2.7.0. It was discovered that the security advisory CVE-2021-36782 (GHSA-g7j7-h4q8-8w2f), previously released by Rancher, missed addressing some sensitive fields, secret tokens, encryption keys, and SSH keys that were still being stored in plaintext directly on Kubernetes objects like `Clusters`.

The exposed credentials are visible in Rancher to authenticated `Cluster Owners`, `Cluster Members`, `Project Owners` and `Project Members` of that cluster on the endpoints:

- `/v1/management.cattle.io.cluster`
- `/v1/management.cattle.io.clustertemplaterevisions`

The remaining sensitive fields are now stripped from `Clusters` and other objects and moved to a `Secret` before the object is stored. The `Secret` is retrieved when the credential is needed. For objects that existed before this security fix, a one-time migration happens on startup.

The fields that have been addressed by this security fix are:

- `Cluster.Spec.RancherKubernetesEngineConfig.Services.KubeAPI.SecretsEncryptionConfig.CustomConfig.Providers[].AESGCM.Keys[].Secret`
- `Cluster.Spec.RancherKubernetesEngineConfig.Services.KubeAPI.SecretsEncryptionConfig.CustomConfig.Providers[].AESCBC.Keys[].Secret`
- `Cluster.Spec.RancherKubernetesEngineConfig.Services.KubeAPI.SecretsEncryptionConfig.CustomConfig.Providers[].SecretboxConfiguration.Keys[].Secret`
- `Cluster.Spec.RancherKubernetesEngineConfig.Services.Kubelet.ExtraEnv` when containing the `AWS_SECRET_ACCESS_KEY` environment variable
- `Cluster.Spec.RancherKubernetesEngineConfig.BastionHost.SSHKey`
- `Cluster.Spec.RancherKubernetesEngineConfig.PrivateRegistries[].ECRCredentialPlugin.AwsSecretAccessKey`
- `Cluster.Spec.RancherKubernetesEngineConfig.PrivateRegistries[].ECRCredentialPlugin.AwsSessionToken`
- `Cluster.Spec.RancherKubernetesEngineConfig.Network.AciNetworkProvider.ApicUserKey`
- `Cluster.Spec.RancherKubernetesEngineConfig.Network.AciNetworkProvider.KafkaClientKey`
- `Cluster.Spec.RancherKubernetesEngineConfig.Network.AciNetworkProvider.Token`

**Important:**

- For the exposure of credentials not related to Rancher, the final impact severity for confidentiality, integrity and availability is dependent on the permissions the leaked credentials have on their services.

- It is recommended to review for potentially leaked credentials in this scenario and to change them if deemed necessary.

### Workarounds

There is no direct mitigation besides updating Rancher to a patched version.

### Patches

Patched versions include releases 2.5.17, 2.6.10, 2.7.1 and later versions.

After upgrading to a patched version, it is important to check for the `ACISecretsMigrated` and `RKESecretsMigrated` conditions on `Clusters` and `ClusterTemplateRevisions` to confirm when secrets have been fully migrated off of those objects, and the objects scoped within them.

### For more information

If you have any questions or comments about this advisory:

* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-cq4p-vp5q-4522
- https://nvd.nist.gov/vuln/detail/CVE-2022-43757
- https://bugzilla.suse.com/show_bug.cgi?id=1205295
- https://github.com/rancher/rancher
