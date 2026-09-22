# [C] RCE on Grafana via sqlExpressions

## Summary
Severity: Critical
Advisory: BIT-grafana-2026-27876
Aliases: CVE-2026-27876
Ecosystem: Bitnami
Published: 2026-04-01
Source: https://osv.dev/vulnerability/BIT-grafana-2026-27876
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.4.0 <12.4.2

## Details
A chained attack via SQL Expressions and a Grafana Enterprise plugin can lead to a remote arbitrary code execution impact (RCE). This is enabled by a feature in Grafana (OSS), so all users are always recommended to update to avoid future attack vectors going this path.

Only instances with the sqlExpressions feature toggle enabled are vulnerable.

Only instances in the following version ranges are affected:

- 11.6.0 (inclusive) to 11.6.14 (exclusive): 11.6.14 has the fix. 11.5 and below are not affected.
- 12.0.0 (inclusive) to 12.1.10 (exclusive): 12.1.10 has the fix. 12.0 did not receive an update, as it is end-of-life.
- 12.2.0 (inclusive) to 12.2.8 (exclusive): 12.2.8 has the fix.
- 12.3.0 (inclusive) to 12.3.6 (exclusive): 12.3.6 has the fix.
- 12.4.0 (inclusive) to 12.4.2 (exclusive): 12.4.2 has the fix. 13.0.0 and above also have the fix: no v13 release is affected.

## References
- https://grafana.com/security/security-advisories/cve-2026-27876
- https://nvd.nist.gov/vuln/detail/CVE-2026-27876
- https://access.redhat.com/security/cve/CVE-2026-27876
- https://bugzilla.redhat.com/show_bug.cgi?id=2452277
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27876.json
