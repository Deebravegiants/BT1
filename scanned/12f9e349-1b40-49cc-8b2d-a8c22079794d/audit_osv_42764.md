# [M] KubeSphere - SSRF via Unvalidated Cluster CRD Connection Endpoint in Cluster Reconciliation

## Summary
Severity: Medium
Advisory: CVE-2026-71208
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71208
Type: osv

## Details
KubeSphere's cluster-controller reconciliation (pkg/utils/clusterclient/clusterclient.go, addCluster) processes every Cluster custom resource's connection configuration and immediately calls Discovery.ServerVersion against the CRD-specified Kubernetes API endpoint, which is parsed only for URL syntax (url.Parse) with no allow/deny-list for loopback, RFC1918 private ranges, link-local, or cloud-metadata addresses (e.g. 169.254.169.254).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71208.json
- https://github.com/ashikmd7/kubeSphere/blob/main/SSRF%20via%20Cluster%20CRD%20KubeConfig/README.md
- https://github.com/kubesphere/kubesphere
- https://nvd.nist.gov/vuln/detail/CVE-2026-71208
