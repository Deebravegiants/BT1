# [M] IDOR in Annotations API allows unprivileged users to DELETE annotation

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-28374
Aliases: CVE-2026-28374
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-grafana-2026-28374
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.1

## Details
Editors could delete any annotation, even those they do not have read access to. The editor user cannot create or read the annotations.

## References
- https://grafana.com/security/security-advisories/cve-2026-28374
- https://nvd.nist.gov/vuln/detail/CVE-2026-28374
