# [M] Submariner Operator sets unnecessary RBAC permissions

## Summary
Severity: Medium
Advisory: GHSA-2rhx-qhxp-5jpw
CVE: CVE-2024-5042
CWE: CWE-250
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2024-05-17
Source: https://github.com/advisories/GHSA-2rhx-qhxp-5jpw
Type: github-advisory

## Affected
- Go: `github.com/submariner-io/submariner-operator` — affected >=0.16.0-m0 <0.16.4
- Go: `github.com/submariner-io/submariner-operator` — affected >=0.17.0-m0 <0.17.2
- Go: `github.com/submariner-io/submariner-operator` — affected >=0 <0.15.4
- Go: `github.com/submariner-io/submariner-operator` — affected >=0.18.0-m0 <0.18.0-rc0

## Details
A flaw was found in the Submariner project. Due to unnecessary role-based access control permissions, a privileged attacker can run a malicious container on a node that may allow them to steal service account tokens and further compromise other nodes and potentially the entire cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5042
- https://github.com/submariner-io/submariner-operator/issues/3041
- https://github.com/submariner-io/submariner-operator/pull/3040
- https://github.com/submariner-io/submariner-operator/pull/3045
- https://github.com/submariner-io/submariner-operator/pull/3046
- https://github.com/submariner-io/submariner-operator/pull/3049
- https://github.com/submariner-io/submariner-operator/commit/b27a04c4270e53cbff6ff8ac6245db10c204bcab
- https://access.redhat.com/errata/RHSA-2024:4591
- https://access.redhat.com/errata/RHSA-2026:6503
- https://access.redhat.com/security/cve/CVE-2024-5042
- https://bugzilla.redhat.com/show_bug.cgi?id=2280921
- https://github.com/advisories/GHSA-2rhx-qhxp-5jpw
- https://github.com/submariner-io/submariner-operator
