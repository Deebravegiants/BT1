# [M] Rancher Backup Operator pod's logs leak S3 tokens

## Summary
Severity: Medium
Advisory: GHSA-wj3p-5h3x-c74q
CVE: CVE-2025-62879
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-wj3p-5h3x-c74q
Type: github-advisory

## Affected
- Go: `github.com/rancher/backup-restore-operator` — affected >=9.0.0 <9.0.1
- Go: `github.com/rancher/backup-restore-operator` — affected >=8.0.0 <8.1.2
- Go: `github.com/rancher/backup-restore-operator` — affected >=7.0.0 <7.0.5
- Go: `github.com/rancher/backup-restore-operator` — affected >=6.0.0 <6.0.3

## Details
### Impact
A vulnerability has been identified within the Rancher Backup Operator, resulting in the leakage of S3 tokens (both `accessKey` and `secretKey`) into the rancher-backup-operator pod's logs.

Specifically, the S3 `accessKey` and `secretKey` are exposed in the pod's logs under the following logging level conditions:

| Variable Exposed | Logging Level Condition | 
------------------ | ------------------------- |
| accessKey            | `trace: false` (default), and `debug: false` (default) |
| secretKey             | `trace: true` or `debug: true`|

**Note:** The S3 `accessKey` is exposed in the logs without requiring any supplementary configuration.

For further information on this attack category, please consult the associated [MITRE ATT&CK - Technique - Log Enumeration](https://attack.mitre.org/techniques/T1654/).

### Patches
This vulnerability is addressed by applying redaction to sensitive information that was leaking.

Patched versions of Rancher Backup Operator include: `108.0.1+up9.0.1`, `107.1.2+up8.1.2`, `106.0.6+up7.0.5`, and `105.0.6+up6.0.3`.

### Workarounds
Users are advised to rotate both S3 `accessKey` and `secretKey` once they have upgraded to a fixed version, especially if logs are exported.

Users who cannot update Rancher are advised to refresh the Rancher app Repository, which should provide the ability to update just the Rancher Backup chart alone. This will patch the vulnerabilities without requiring Rancher to be updated. This will not work for Rancher clusters in an air-gap setup.

For air-gapped Rancher clusters, the Rancher version must be updated first, and then after you will find the patched version of the Rancher Backup chart to upgrade. You will also need to sync new images for the release to your image mirror.

Users who cannot update either Rancher or Rancher Backup should ensure that both debug and trace values are both false (default). Users should revert the values to the default until they can update to prevent potential leaks.

### References
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/backup-restore-operator/security/advisories/GHSA-wj3p-5h3x-c74q
- https://nvd.nist.gov/vuln/detail/CVE-2025-62879
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-62879
- https://github.com/rancher/backup-restore-operator
