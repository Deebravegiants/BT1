# [H] Kubean vulnerable to cluster-level privilege escalation

## Summary
Severity: High
Advisory: GHSA-3wfj-3x8q-hrpg
CVE: CVE-2024-41820
CWE: CWE-276, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-3wfj-3x8q-hrpg
Type: github-advisory

## Affected
- Go: `github.com/kubean-io/kubean` — affected >=0 <0.18.0

## Details
### Impact
This ClusterRole has `*` verbs of `*` resources. If a malicious user can access the worker node which has kubean's deployment, he/she can abuse these excessive permissions to do whatever he/she likes to the whole cluster, resulting in a cluster-level privilege escalation.

### Patches
>=v0.18.0

### References
Reporting by @younaman(Nanzi Yang)
https://github.com/kubean-io/kubean/issues/1326

## References
- https://github.com/kubean-io/kubean/security/advisories/GHSA-3wfj-3x8q-hrpg
- https://nvd.nist.gov/vuln/detail/CVE-2024-41820
- https://github.com/kubean-io/kubean/issues/1326
- https://github.com/kubean-io/kubean/commit/167e97329e4a27ba2f456d2846d39af20e1af7ef
- https://github.com/kubean-io/kubean
- https://pkg.go.dev/vuln/GO-2024-3039
