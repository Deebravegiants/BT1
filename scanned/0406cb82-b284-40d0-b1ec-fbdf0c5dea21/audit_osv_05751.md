# [M] SAML assertion replay via skipped InResponseTo validation

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-12704
Aliases: CVE-2026-12704
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-grafana-2026-12704
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.2.0 <13.2.1

## Details
When SAML IdP-initiated login is enabled in Grafana Enterprise, the SAML library skips validation of the InResponseTo field on all SAML responses, including SP-initiated logins. This removes anti-replay protection, allowing an attacker who obtains a valid signed SAML assertion to replay it and gain a session as the victim user. Only instances with the allow_idp_initiated SAML setting enabled are affected; this setting is off by default and Grafana OSS is not affected.

## References
- https://grafana.com/security/security-advisories/cve-2026-12704
- https://nvd.nist.gov/vuln/detail/CVE-2026-12704
