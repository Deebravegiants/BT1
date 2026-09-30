# [H] Rancher: Cross-Cluster Secret Leakage via Namespace projectId Annotation Spoofing

## Summary
Severity: High
Advisory: CVE-2026-75033
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-75033
Type: osv

## Details
A flaw was found in Rancher Manager. Project Secrets were propagated into a namespace based only on its `field.cattle.io/projectId` annotation, without verifying that the referenced project belonged to the same downstream cluster. A user able to create namespaces on one cluster could set the annotation to a project ID from another cluster and have that project's secrets copied into a namespace under their control.


This issue affects Rancher: before 2.15.1.

## References
- https://github.com/rancher/rancher/releases/tag/v2.15.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75033.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75033
- https://github.com/rancher/rancher
