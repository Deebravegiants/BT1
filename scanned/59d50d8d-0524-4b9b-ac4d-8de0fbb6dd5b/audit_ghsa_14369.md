# [H]  OpenFeature Operator vulnerable to Cluster-level Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-cwf6-xj49-wp83
CVE: CVE-2023-29018
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-cwf6-xj49-wp83
Type: github-advisory

## Affected
- Go: `github.com/open-feature/open-feature-operator` — affected >=0 <0.2.32

## Details
### Impact

On a node controlled by an attacker or malicious user, the lax permissions configured on `open-feature-operator-controller-manager` can be used to further escalate the privileges of any service account in the cluster.

The increased privileges could be used to modify cluster state, leading to DoS, or read sensitive data, including secrets.

### Patches

The patch mitigates this issue by restricting the resources the `open-feature-operator-controller-manager` can modify.

## References
- https://github.com/open-feature/open-feature-operator/security/advisories/GHSA-cwf6-xj49-wp83
- https://nvd.nist.gov/vuln/detail/CVE-2023-29018
- https://github.com/open-feature/open-feature-operator
- https://github.com/open-feature/open-feature-operator/releases/tag/v0.2.32
