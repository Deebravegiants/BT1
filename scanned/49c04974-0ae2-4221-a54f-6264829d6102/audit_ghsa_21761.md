# [M] Directory traversal in Kubernetes Secrets Store CSI Driver

## Summary
Severity: Medium
Advisory: GHSA-5cgx-vhfp-6cf9
CVE: CVE-2020-8568
CWE: CWE-20, CWE-22, CWE-24
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-5cgx-vhfp-6cf9
Type: github-advisory

## Affected
- Go: `sigs.k8s.io/secrets-store-csi-driver` — affected >=0.0.15 <0.0.17

## Details
Kubernetes Secrets Store CSI Driver versions v0.0.15 and v0.0.16 allow an attacker who can modify a `SecretProviderClassPodStatus/Status` resource the ability to write content to the host filesystem and sync file contents to Kubernetes Secrets. This includes paths under `var/lib/kubelet/pods` that contain other Kubernetes Secrets.

### Specific Go Packages Affected
sigs.k8s.io/secrets-store-csi-driver/controllers
sigs.k8s.io/secrets-store-csi-driver/pkg/rotation
sigs.k8s.io/secrets-store-csi-driver/pkg/secrets-store

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8568
- https://github.com/kubernetes-sigs/secrets-store-csi-driver/issues/378
- https://github.com/kubernetes-sigs/secrets-store-csi-driver/pull/371
- https://github.com/kubernetes-sigs/secrets-store-csi-driver/commit/c2cbb19e2eef16638fa0523383788a4bc22231fd
- https://github.com/kubernetes-sigs/secrets-store-csi-driver
- https://groups.google.com/g/kubernetes-secrets-store-csi-driver/c/Cb9cvymTzl4
- https://pkg.go.dev/vuln/GO-2022-0629
