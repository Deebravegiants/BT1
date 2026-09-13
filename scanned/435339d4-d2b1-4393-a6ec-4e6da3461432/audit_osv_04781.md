# [H] Envoy crashes when idle and request per try timeout occur within the backoff interval

## Summary
Severity: High
Advisory: BIT-envoy-2024-23322
Aliases: CVE-2024-23322, GHSA-6p83-mfmh-qv38
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2024-23322
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.29.0 <1.29.1

## Details
Envoy is a high-performance edge/middle/service proxy. Envoy will crash when certain timeouts happen within the same interval. The crash occurs when the following are true: 1. hedge_on_per_try_timeout is enabled, 2. per_try_idle_timeout is enabled (it can only be done in configuration), 3. per-try-timeout is enabled, either through headers or configuration and its value is equal, or within the backoff interval of the per_try_idle_timeout. This issue has been addressed in released 1.29.1, 1.28.1, 1.27.3, and 1.26.7. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/envoyproxy/envoy/commit/843f9e6a123ed47ce139b421c14e7126f2ac685e
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-6p83-mfmh-qv38
- https://nvd.nist.gov/vuln/detail/CVE-2024-23322
