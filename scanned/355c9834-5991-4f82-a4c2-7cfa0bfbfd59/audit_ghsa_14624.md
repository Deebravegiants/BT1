# [H] OpenShift Hive RCE through AWS/Kubernetes client configuration leads to privilege escalation

## Summary
Severity: High
Advisory: GHSA-wgqq-9qh8-wvqv
CVE: CVE-2024-25133
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-31
Source: https://github.com/advisories/GHSA-wgqq-9qh8-wvqv
Type: github-advisory

## Affected
- Go: `github.com/openshift/hive` — affected >=0

## Details
A flaw was found in the Hive ClusterDeployments resource in OpenShift Dedicated. In certain conditions, this issue may allow a developer account on a Hive-enabled cluster to obtain cluster-admin privileges by executing arbitrary commands on the hive/hive-controllers pod.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25133
- https://github.com/openshift/hive/pull/2306
- https://github.com/openshift/hive/commit/5ba846620f9dbf49301dabb0d40cc980aabef4e0
- https://access.redhat.com/security/cve/CVE-2024-25133
- https://bugzilla.redhat.com/show_bug.cgi?id=2260372
- https://github.com/openshift/hive
