# [M] CVE-2020-8567

## Summary
Severity: Medium
Advisory: CVE-2020-8567
Aliases: GHSA-2v35-wj4r-rcmv, GO-2024-2750
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-01-21
Source: https://osv.dev/vulnerability/CVE-2020-8567
Type: osv

## Details
Kubernetes Secrets Store CSI Driver Vault Plugin prior to v0.0.6, Azure Plugin prior to v0.0.10, and GCP Plugin prior to v0.2.0 allow an attacker who can create specially-crafted SecretProviderClass objects to write to arbitrary file paths on the host filesystem, including /var/lib/kubelet/pods.

## References
- https://groups.google.com/g/kubernetes-secrets-store-csi-driver/c/BI2qisiNXHY
- https://github.com/kubernetes-sigs/secrets-store-csi-driver/issues/384
