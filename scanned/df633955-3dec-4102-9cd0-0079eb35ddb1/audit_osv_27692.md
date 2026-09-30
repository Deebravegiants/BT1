# [M] SSRF in Sentry via Phabricator integration

## Summary
Severity: Medium
Advisory: CVE-2024-24829
Aliases: GHSA-rqxh-fp9p-p98r
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-02-08
Source: https://osv.dev/vulnerability/CVE-2024-24829
Type: osv

## Details
Sentry is an error tracking and performance monitoring platform. Sentry’s integration platform provides a way for external services to interact with Sentry. One of such integrations, the Phabricator integration (maintained by Sentry) with version <=24.1.1 contains a constrained SSRF vulnerability. An attacker could make Sentry send POST HTTP requests to arbitrary URLs (including internal IP addresses) by providing an unsanitized input to the Phabricator integration. However, the body payload is constrained to a specific format. If an attacker has access to a Sentry instance, this allows them to: 1. interact with internal network; 2. scan local/remote ports. This issue has been fixed in Sentry self-hosted release 24.1.2, and has already been mitigated on sentry.io on February 8. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/getsentry/self-hosted/releases/tag/24.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24829.json
- https://github.com/getsentry/sentry/security/advisories/GHSA-rqxh-fp9p-p98r
- https://nvd.nist.gov/vuln/detail/CVE-2024-24829
- https://github.com/getsentry/sentry/pull/64882
