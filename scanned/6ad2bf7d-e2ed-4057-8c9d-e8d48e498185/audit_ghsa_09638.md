# [M] KubeVirt's authorization mechanism improperly truncates subresource names

## Summary
Severity: Medium
Advisory: GHSA-j6cv-3w8p-vrg8
CVE: CVE-2026-6383
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-j6cv-3w8p-vrg8
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0

## Details
A flaw was found in KubeVirt's Role-Based Access Control (RBAC) evaluation logic. The authorization mechanism improperly truncates subresource names, leading to incorrect permission evaluations. This allows authenticated users with specific custom roles to gain unauthorized access to subresources, potentially disclosing sensitive information or performing actions they are not permitted to do. Additionally, legitimate users may be denied access to resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6383
- https://github.com/kubevirt/kubevirt/issues/17337
- https://access.redhat.com/security/cve/CVE-2026-6383
- https://bugzilla.redhat.com/show_bug.cgi?id=2458741
- https://github.com/kubevirt/kubevirt
