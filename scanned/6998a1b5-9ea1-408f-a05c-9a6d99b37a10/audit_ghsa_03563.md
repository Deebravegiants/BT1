# [M] Cross-site scripting (XSS) vulnerability in the password reset endpoint

## Summary
Severity: Medium
Advisory: GHSA-246w-56m2-5899
CVE: CVE-2021-21332
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-03-26
Source: https://github.com/advisories/GHSA-246w-56m2-5899
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.27.0

## Details
### Impact
The password reset endpoint served via Synapse was vulnerable to cross-site scripting (XSS) attacks. The impact depends on the configuration of the domain that Synapse is deployed on, but may allow access to cookies and other browser data, CSRF vulnerabilities, and access to other resources served on the same domain or parent domains.

### Patches
This is fixed in #9200.

### Workarounds
Depending on the needs and configuration of the homeserver a few options are available:

1. Password resets can be disabled by delegating email to a third-party service (via the `account_threepid_delegates.email` setting) or disabling email (by not configuring the `email` setting).

2. If the homeserver is not configured to use passwords (via the `password_config.enabled` setting) then the affected endpoint can be blocked at a reverse proxy:

    * `/_synapse/client/password_reset/email/submit_token`

3. The `password_reset_confirmation.html` template can be overridden with a custom template that manually escapes the variables using [JInja2's `escape` filter](https://jinja.palletsprojects.com/en/2.11.x/templates/#escape). See the `email.template_dir` setting.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-246w-56m2-5899
- https://nvd.nist.gov/vuln/detail/CVE-2021-21332
- https://github.com/matrix-org/synapse/pull/9200
- https://github.com/matrix-org/synapse/commit/e54746bdf7d5c831eabe4dcea76a7626f1de73df
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.27.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-133.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY
