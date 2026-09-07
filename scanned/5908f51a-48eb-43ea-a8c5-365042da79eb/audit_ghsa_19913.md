# [H] Openshift Hive Exposes VCenter Credentials via ClusterProvision

## Summary
Severity: High
Advisory: GHSA-c339-mwfc-fmr2
CVE: CVE-2025-2241
CWE: CWE-922
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-17
Source: https://github.com/advisories/GHSA-c339-mwfc-fmr2
Type: github-advisory

## Affected
- Go: `github.com/openshift/hive` — affected >=0

## Details
A flaw was found in Hive, a component of Multicluster Engine (MCE) and Advanced Cluster Management (ACM). This vulnerability causes VCenter credentials to be exposed in the ClusterProvision object after provisioning a VSphere cluster. Users with read access to ClusterProvision objects can extract sensitive credentials even if they do not have direct access to Kubernetes Secrets. This issue can lead to unauthorized VCenter access, cluster management, and privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2241
- https://github.com/openshift/hive/pull/2612
- https://access.redhat.com/security/cve/CVE-2025-2241
- https://bugzilla.redhat.com/show_bug.cgi?id=2351350
- https://github.com/openshift/hive
