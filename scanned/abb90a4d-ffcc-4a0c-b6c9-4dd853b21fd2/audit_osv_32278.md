# [M] JumpServer has a Kubernetes Token Leak Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-27095
Aliases: GHSA-5q9w-f4wh-f535
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-03-31
Source: https://osv.dev/vulnerability/CVE-2025-27095
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. Prior to 4.8.0 and 3.10.18, an attacker with a low-privileged account can access the Kubernetes session feature and manipulate the kubeconfig file to redirect API requests to an external server controlled by the attacker. This allows the attacker to intercept and capture the Kubernetes cluster token. This can potentially allow unauthorized access to the cluster and compromise its security. This vulnerability is fixed in 4.8.0 and 3.10.18.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27095.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-5q9w-f4wh-f535
- https://nvd.nist.gov/vuln/detail/CVE-2025-27095
