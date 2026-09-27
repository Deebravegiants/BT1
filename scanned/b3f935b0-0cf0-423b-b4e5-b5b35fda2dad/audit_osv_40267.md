# [H] Sentry: Inefficient Regular Expression Complexity in sentry

## Summary
Severity: High
Advisory: CVE-2026-52794
Aliases: GHSA-jjqr-wqg2-p856
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52794
Type: osv

## Details
Sentry is an error tracking and performance monitoring tool. From 24.4.0 until 26.5.2, a Regular Expression Denial of Service (ReDoS) vulnerability exists in Sentry's event ingestion pipeline, where a regex applied to attacker-controlled fields on incoming events can be made to consume disproportionate CPU time. This vulnerability is fixed in 26.5.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52794.json
- https://github.com/getsentry/sentry/security/advisories/GHSA-jjqr-wqg2-p856
- https://nvd.nist.gov/vuln/detail/CVE-2026-52794
- https://github.com/getsentry/sentry/pull/116587
