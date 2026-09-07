# [H] Rancher's RKE1 Encryption Config kept in plain-text within cluster AppliedSpec

## Summary
Severity: High
Advisory: GHSA-q6c7-56cq-g2wm
CVE: CVE-2024-22032
CWE: CWE-200, CWE-256
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-q6c7-56cq-g2wm
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.7.0 <2.7.14
- Go: `github.com/rancher/rancher` — affected >=2.8.0 <2.8.5

## Details
### Impact
This issue is only relevant to clusters provisioned using RKE1 with secrets encryption configuration enabled.

A vulnerability has been identified in which an RKE1 cluster keeps constantly reconciling when secrets encryption configuration is enabled (please see the [RKE documentation](https://rke.docs.rancher.com/config-options/secrets-encryption)). When reconciling, the Kube API secret values are written in plaintext on the AppliedSpec. Cluster owners, Cluster members, and Project members (for projects within the cluster), all have RBAC permissions to view the cluster object from the apiserver.

This could lead to an unauthorized user gaining access to the entire secrets encryption config specific for the cluster, only on the applied spec.

Since this affects only custom encryption configurations, users need to manually rotate the keys by editing the cluster. For more information, please refer to the [RKE secrets encryption documentation](https://rke.docs.rancher.com/config-options/secrets-encryption#key-rotation).

The full custom configuration example:

```yaml
services:
  kube-api:
    secrets_encryption_config:
      enabled: true
      custom_config:
        apiVersion: apiserver.config.k8s.io/v1
        kind: EncryptionConfiguration
        resources:
        - resources:
          - secrets
          providers:
          - aescbc:
              keys:
              - name: k-fw5hn
                secret: RTczRjFDODMwQzAyMDVBREU4NDJBMUZFNDhCNzM5N0I= #<--- needs to be changed
          - identity: {}
```

Please consult the associated  [MITRE ATT&CK - Technique - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/) for further information about this category of attack.

### Patches
To address this issue, the fix introduces a new change that copies the AppliedSpec before mutating. As such, the next time the cluster is reconciled and the AppliedSpec is set, all references to sensitive data will be removed. 

Patched versions include releases `2.7.14` and `2.8.5`.

### Workarounds
There are no workarounds for this issue. Users are recommended to upgrade, as soon as possible, to a version of RKE/Rancher Manager which contains the fixes. 

### References
- [CVE-2024-22032](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-22032)

If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security-related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-q6c7-56cq-g2wm
- https://nvd.nist.gov/vuln/detail/CVE-2024-22032
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2024-22032
- https://github.com/rancher/rancher
