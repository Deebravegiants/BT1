# [M] Appsmith: SSRF via `POST /api/v1/admin/send-test-email` — JavaMail Bypasses WebClient IP Filter

## Summary
Severity: Medium
Advisory: BIT-appsmith-2026-49979
Aliases: BIT-appsmith-2026-7299, CVE-2026-49979, CVE-2026-7299, GHSA-vvxf-f8q9-86gh
Ecosystem: Bitnami
Published: 2026-06-30
Source: https://osv.dev/vulnerability/BIT-appsmith-2026-49979
Type: osv

## Affected
- Bitnami: `appsmith` — affected >=0 <1.99.0

## Details
Appsmith is a platform to build admin panels, internal tools, and dashboards. Prior to 1.99, the POST /api/v1/admin/send-test-email endpoint accepts attacker-controlled smtpHost and smtpPort values and establishes a raw JavaMail TCP connection without any IP validation. This completely bypasses WebClientUtils.IP_CHECK_FILTER, which only applies to Spring WebClient HTTP requests. Additionally, the raw MailException.getMessage() is returned verbatim in the API error response, enabling error-based internal port scanning and service banner enumeration. This vulnerability is fixed in 1.99.

## References
- https://github.com/appsmithorg/appsmith/security/advisories/GHSA-vvxf-f8q9-86gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-49979
