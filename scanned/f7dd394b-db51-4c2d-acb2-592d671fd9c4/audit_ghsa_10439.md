# [M] Amazon EFS CSI Driver has mount option injection via unsanitized volumeHandle and mounttargetip fields

## Summary
Severity: Medium
Advisory: GHSA-mph4-q2vm-w2pw
CVE: CVE-2026-6437
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-mph4-q2vm-w2pw
Type: github-advisory

## Affected
- Go: `github.com/kubernetes-sigs/aws-efs-csi-driver` — affected >=0 <1.7.8-0.20260416142831-51806c22c575

## Details
### Summary
The Amazon EFS CSI Driver is a Container Storage Interface driver that allows Kubernetes clusters to use Amazon Elastic File System. An issue exists where, under certain circumstances, unsanitized values in the volumeHandle and mounttargetip fields are passed directly to the mount command, allowing injection of arbitrary mount options.

### Impact
An actor with PersistentVolume creation privileges can inject arbitrary mount options by appending comma-separated values to the Access Point ID in volumeHandle or to the mounttargetip volumeAttribute. The mount utility parses comma-separated values as separate options, causing the injected options to be applied to the filesystem mount without authorization.

Impacted versions: <= v3.0.0

### Patches
This issue has been addressed in Amazon EFS CSI Driver version v3.0.1. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Restrict PersistentVolume and StorageClass creation to cluster administrators using Kubernetes RBAC, preventing untrusted users from supplying arbitrary field values.

### References
If you have any questions or comments about this advisory, we ask that you contact AWS Security via our vulnerability reporting page or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com).  Please do not create a public GitHub issue.

### Acknowledgement
We would like to thank Shaul Ben-Hai from Sentinel One for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/kubernetes-sigs/aws-efs-csi-driver/security/advisories/GHSA-mph4-q2vm-w2pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-6437
- https://github.com/kubernetes-sigs/aws-efs-csi-driver/commit/51806c22c5754bfbdeca6910f15571a07921b784
- https://aws.amazon.com/security/security-bulletins/2026-016-aws
- https://github.com/kubernetes-sigs/aws-efs-csi-driver
- https://github.com/kubernetes-sigs/aws-efs-csi-driver/releases/tag/v3.0.1
