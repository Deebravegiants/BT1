# [M] Aiven Operator has cross-namespace secret exfiltration via ClickhouseUser connInfoSecretSource

## Summary
Severity: Medium
Advisory: GHSA-99j8-wv67-4c72
CVE: CVE-2026-39961
CWE: CWE-269, CWE-441
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-99j8-wv67-4c72
Type: github-advisory

## Affected
- Go: `github.com/aiven/aiven-operator` — affected >=0.31.0 <0.37.0

## Details
### Impact
A developer with create permission on ClickhouseUser CRDs in their own namespace can exfiltrate secrets from any other namespace — production database credentials, API keys, service tokens — with a single kubectl apply. The operator reads the victim's secret using its ClusterRole and writes the password into a new secret in the attacker's namespace.

The operator acts as a confused deputy: its ServiceAccount has cluster-wide secret read/write (aiven-operator-role ClusterRole), and it trusts user-supplied namespace values in spec.connInfoSecretSource.namespace without validation. No admission webhook enforces this boundary — the ServiceUser webhook returns nil, and no ClickhouseUser webhook exists.

### Patches

This vulnerability is resolved in version 0.37.0. We recommend all users update as soon as possible.

### Credits

Credits to Andrés Cruciani for finding and reporting the bug through our [bug bounty program](https://bugcrowd.com/aiven-mbb-og)

## References
- https://github.com/aiven/aiven-operator/security/advisories/GHSA-99j8-wv67-4c72
- https://nvd.nist.gov/vuln/detail/CVE-2026-39961
- https://github.com/aiven/aiven-operator/commit/032c9ba63257fdd2fddfb7f73f71830e371ff182
- https://github.com/aiven/aiven-operator
- https://github.com/aiven/aiven-operator/releases/tag/v0.37.0
