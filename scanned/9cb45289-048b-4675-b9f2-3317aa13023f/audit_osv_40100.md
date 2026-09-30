# [H] Fission: Cross-namespace Environment reference in Package allows build-time command execution and SA token exfiltration

## Summary
Severity: High
Advisory: CVE-2026-49821
Aliases: GHSA-vjhc-cf4p-72q4, GO-2026-5859
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-49821
Type: osv

## Details
Fission is an open-source, Kubernetes-native serverless framework that simplifies the deployment of functions and applications on Kubernetes. Prior to version 1.24.0, Fission's buildermgr controller processed Package CRDs without verifying that Package.spec.environment.namespace matched Package.metadata.namespace. This issue has been patched in version 1.24.0.

## References
- https://github.com/fission/fission/releases/tag/v1.24.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49821.json
- https://github.com/fission/fission/security/advisories/GHSA-vjhc-cf4p-72q4
- https://nvd.nist.gov/vuln/detail/CVE-2026-49821
- https://github.com/fission/fission/pull/3379
