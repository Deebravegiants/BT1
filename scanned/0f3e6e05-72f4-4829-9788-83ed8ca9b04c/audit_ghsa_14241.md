# [M] A potential risk in clusternet which can be leveraged to make a cluster-level privilege escalation

## Summary
Severity: Medium
Advisory: GHSA-833c-xh79-p429
CVE: CVE-2023-30622
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-833c-xh79-p429
Type: github-advisory

## Affected
- Go: `github.com/clusternet/clusternet` — affected >=0 <0.15.2

## Details
## Summary:
A potential risk in clusternet which can be leveraged to make a cluster-level privilege escalation.
## Detailed analysis:
The clusternet has a deployment called cluster-hub inside the clusternet-system Kubernetes namespace, which runs on worker nodes
randomly. The deployment has a service account called clusternet-hub, which has a cluster role called clusternet:hub via cluster role binding. The clusternet:hub cluster role has "*" verbs of "*.*" resources. Thus, if a malicious user can access the worker node which runs the clusternet, he/she can leverage the service account to do malicious actions to critical system resources. For example, he/she can leverage the service account to get ALL secrets in the entire cluster, resulting in cluster-level privilege escalation.

## References
- https://github.com/clusternet/clusternet/security/advisories/GHSA-833c-xh79-p429
- https://nvd.nist.gov/vuln/detail/CVE-2023-30622
- https://github.com/clusternet/clusternet
- https://github.com/clusternet/clusternet/releases/tag/v0.15.2
