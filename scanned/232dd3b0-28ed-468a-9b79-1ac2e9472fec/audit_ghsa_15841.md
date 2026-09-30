# [H] Exposure of vSphere's CPI and CSI credentials in Rancher

## Summary
Severity: High
Advisory: GHSA-xj7w-r753-vj8v
CVE: CVE-2022-45157
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2024-10-25
Source: https://github.com/advisories/GHSA-xj7w-r753-vj8v
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.9.0 <2.9.3
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.8.9

## Details
### Impact

A vulnerability has been identified in the way that Rancher stores vSphere's CPI (Cloud Provider Interface) and CSI (Container Storage Interface) credentials used to deploy clusters through the vSphere cloud provider. This issue leads to the vSphere CPI and CSI passwords being stored in a plaintext object inside Rancher. This vulnerability is only applicable to users that deploy clusters in vSphere environments.

The exposed passwords were accessible in the following objects:

- Can be accessed by users that are cluster members of the provisioned clusters:
  - When provisioning a new cluster with the vSphere cloud provider through Rancher's UI (user interface), Cluster Templates and Terraform on the object `provisioning.cattle.io` in `spec.rkeConfig.chartValues.rancher-vsphere-cpi` and `spec.rkeConfig.chartValues.rancher-vsphere-csi`.
  - On the object `rke.cattle.io.rkecontrolplane` in `spec.chartValues.rancher-vsphere-cpi` and `spec.chartValues.rancher-vsphere-csi`.
- Can be accessed by users with privileged access to the clusters' infrastructure (host OS):
  - Inside the `plan` files in the provisioned downstream clusters' filesystems.

**Note:** if you believe that the vSphere credentials might have been accessed by unauthorized users, it's highly recommended to change them, after updating Rancher to a patched version.

Please consult the associated  [MITRE ATT&CK - Technique -  Credential Access](https://attack.mitre.org/tactics/TA0006/) for further information about this category of attack.

### Patches

Patched versions include Rancher releases **2.8.9 and 2.9.3**.

After updating your environment to one of the patched Rancher's versions, it's mandatory to execute [this script](https://github.com/rancherlabs/support-tools/tree/master/migrate-vsphere-clusters) that provides an automated way to mitigate any vulnerable leftover vSphere clusters' credentials within Rancher's local cluster. This script doesn't need to be executed in case you are installing a fresh and new environment.

The script will fetch all objects in Rancher's local cluster,  loops through them, if the affected vSphere charts are present, then it extracts the `username` and `password` parameters into a secret in the `fleet-default` namespace for both with the appropriate annotation to synchronize them to the downstream clusters. Finally, it updates the cluster's `chartValues` to reference those secrets rather than existing plaintext values.

The script confirms on write operations, as well as backs up configurations of the cluster objects before operating so rolling back is simple.

To run the script, fetch the `kubeconfig` for your local cluster and run with `KUBECONFIG=/path/to/kubeconfig.yml bash migrate.sh`. The script is idempotent and can be run multiple times safely if you want to validate just one at a time.

**Notes:**

- The [feature flag](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/installation-references/feature-flags) `provisioningprebootstrap` must be enabled after updating to one of the patched versions. This feature flag is also mandatory when installing a new cluster.
- **Rancher 2.7 release line is not receiving a backport security patch for this vulnerability.** For users running Rancher 2.7 with vSphere provisioning and that are concerned with this security issue, the recommendation is to update Rancher to one of the patched versions by following the standard update procedure based on the 2.7 version that is being used. Refer to the release notes for the proper update process for [2.8.9](https://github.com/rancher/rancher/releases/tag/v2.8.9) and [2.9.3](https://github.com/rancher/rancher/releases/tag/v2.9.3).

### Workarounds

Besides only granting access to Rancher to trusted users and not allowing direct access to untrusted users to the clusters' infrastructure, there is no direct workaround for this security issue, except updating Rancher to one of the patched versions.

### References

If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-xj7w-r753-vj8v
- https://nvd.nist.gov/vuln/detail/CVE-2022-45157
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2022-45157
- https://github.com/rancher/rancher
