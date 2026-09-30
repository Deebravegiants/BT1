# [M] Helm Files.Lines Denial of Service via Empty Chart Files

## Summary
Severity: Medium
Advisory: BIT-helm-2026-63308
Aliases: CVE-2026-63308
Ecosystem: Bitnami
Published: 2026-07-31
Source: https://osv.dev/vulnerability/BIT-helm-2026-63308
Type: osv

## Affected
- Bitnami: `helm` — affected >=0 <4.2.4

## Details
Helm through 4.2.3, fixed in commit ba6c9a2, contains a denial of service vulnerability in the Files.Lines template helper in pkg/engine/files.go that allows attackers to trigger an index out of range panic by including zero-length byte slices in chart files. Attackers can include empty files in Helm charts to cause deterministic render failures across template, install, upgrade, lint, and SDK Engine.Render operations.

## References
- https://github.com/helm/helm/commit/ba6c9a29efa7bf9198dad6a5ec12b4fb30c96017
- https://github.com/helm/helm/issues/32279
- https://github.com/helm/helm/pull/32290
- https://nvd.nist.gov/vuln/detail/CVE-2026-63308
- https://www.vulncheck.com/advisories/chat2db-insecure-direct-object-reference-via-get-api-connection-datasource
