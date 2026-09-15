# [H] Sentry: Superusers can execute arbitrary commands by injecting malicious pickle-serialized objects through audit log entry data parameter

## Summary
Severity: High
Advisory: GHSA-444r-2whx-3685
CVE: CVE-2021-47935
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-10
Source: https://github.com/advisories/GHSA-444r-2whx-3685
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=0 <8.1.4
- PyPI: `sentry` — affected >=8.2.0 <8.2.2

## Details
Sentry 8.2.0 contains a remote code execution vulnerability that allows authenticated superusers to execute arbitrary commands by injecting malicious pickle-serialized objects through the audit log entry data parameter. Attackers can submit crafted POST requests to the admin audit log endpoint with base64-encoded compressed pickle payloads in the data field to achieve code execution with application privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-47935
- https://github.com/getsentry/sentry/commit/19a0ba63d9ffb6aff79c7b78e2fa951a94edd61a
- https://github.com/getsentry/sentry/commit/1f6090dc64b237c3da22bf35a5863a7136ac4669
- https://github.com/getsentry/sentry
- https://github.com/pypa/advisory-database/tree/main/vulns/sentry/PYSEC-2026-131.yaml
- https://sentry.io/welcome
- https://www.exploit-db.com/exploits/50318
- https://www.vulncheck.com/advisories/sentry-remote-code-execution-via-pickle-deserialization
