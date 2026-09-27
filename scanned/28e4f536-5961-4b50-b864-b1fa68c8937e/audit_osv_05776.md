# [H] CVE-2026-75889 CVE Record

## Summary
Severity: High
Advisory: BIT-grafana-alloy-2026-75889
Aliases: CVE-2026-75889
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-grafana-alloy-2026-75889
Type: osv

## Affected
- Bitnami: `grafana-alloy` — affected >=1.0.0 <1.19.0

## Details
Grafana Alloy’s prometheus.operator.servicemonitors component allows a user who can create or modify ServiceMonitor resources in a watched namespace to specify an arbitrary local file through bearerTokenFile. Alloy reads the file and sends its contents as a bearer token to an attacker-controlled scrape endpoint. This may disclose files accessible to the Alloy process, including its projected Kubernetes service account token, potentially granting the attacker Alloy’s Kubernetes permissions. Exploitation requires ServiceMonitor write access and lower privileges than Alloy’s service account.

## References
- https://grafana.com/security/security-advisories/cve-2026-75889
- https://nvd.nist.gov/vuln/detail/CVE-2026-75889
