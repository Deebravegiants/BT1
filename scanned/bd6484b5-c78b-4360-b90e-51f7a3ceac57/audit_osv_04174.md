# [C] Account Takeover Vulnerability in Appsmith

## Summary
Severity: Critical
Advisory: BIT-appsmith-2026-22794
Aliases: CVE-2026-22794, GHSA-7hf5-mc28-xmcv
Ecosystem: Bitnami
Published: 2026-01-14
Source: https://osv.dev/vulnerability/BIT-appsmith-2026-22794
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.93.0

## Details
Appsmith is a platform to build admin panels, internal tools, and dashboards. Prior to 1.93, the server uses the Origin value from the request headers as the email link baseUrl without validation. If an attacker controls the Origin, password reset / email verification links in emails can be generated pointing to the attacker’s domain, causing authentication tokens to be exposed and potentially leading to account takeover. This vulnerability is fixed in 1.93.

## References
- https://github.com/appsmithorg/appsmith/commit/6f9ee6226bac13fb4b836940b557913fff78b633
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-7hf5-mc28-xmcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-22794
