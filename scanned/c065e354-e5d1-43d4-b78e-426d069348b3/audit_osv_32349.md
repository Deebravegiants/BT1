# [M] Tempo-operator: serviceaccount token exposure leading to token and subject access reviews in openshift tempo operator

## Summary
Severity: Medium
Advisory: CVE-2025-2786
Aliases: GHSA-28gr-56hr-prp6, GO-2026-4996
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-2786
Type: osv

## Details
A flaw was found in Tempo Operator, where it creates a ServiceAccount, ClusterRole, and ClusterRoleBinding when a user deploys a TempoStack or TempoMonolithic instance. This flaw allows a user with full access to their namespace to extract the ServiceAccount token and use it to submit TokenReview and SubjectAccessReview requests, potentially revealing information about other users' permissions. While this does not allow privilege escalation or impersonation, it exposes information that could aid in gathering information for further attacks.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2025:3607
- https://access.redhat.com/errata/RHSA-2025:3740
- https://access.redhat.com/security/cve/CVE-2025-2786
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2786.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2786
- https://bugzilla.redhat.com/show_bug.cgi?id=2354811
- https://github.com/grafana/tempo-operator/pull/1145
- https://github.com/grafana/tempo-operator
