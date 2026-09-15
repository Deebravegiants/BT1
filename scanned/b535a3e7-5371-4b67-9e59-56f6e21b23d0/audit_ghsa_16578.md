# [M] azure-file-csi-driver leaks service account tokens in the logs

## Summary
Severity: Medium
Advisory: GHSA-qjqg-4wg7-957h
CVE: CVE-2024-3744
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-qjqg-4wg7-957h
Type: github-advisory

## Affected
- Go: `sigs.k8s.io/azurefile-csi-driver` — affected >=0 <1.29.4
- Go: `sigs.k8s.io/azurefile-csi-driver` — affected >=1.30.0 <1.30.1

## Details
A security issue was discovered in azure-file-csi-driver where an actor with access to the driver logs could observe service account tokens. These tokens could then potentially be exchanged with external cloud providers to access secrets stored in cloud vault solutions. Tokens are only logged when TokenRequests is configured in the CSIDriver object and the driver is set to run at log level 2 or greater via the -v flag.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3744
- https://github.com/kubernetes/kubernetes/issues/124759
- https://github.com/kubernetes-sigs/azurefile-csi-driver/commit/a1b7446de942136419f07394efeef804523f87ae
- https://github.com/kubernetes-sigs/azurefile-csi-driver/commit/e11ff3dc2c03894cde692213308f9991e7bbd5bf
- https://github.com/kubernetes-sigs/azurefile-csi-driver
- https://groups.google.com/g/kubernetes-security-announce/c/hcgZE2MQo1A/m/Y4C6q-CYAgAJ
- http://www.openwall.com/lists/oss-security/2024/05/09/4
