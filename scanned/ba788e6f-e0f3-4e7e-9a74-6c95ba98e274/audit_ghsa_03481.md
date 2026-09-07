# [M] HTML injection in email and account expiry notifications

## Summary
Severity: Medium
Advisory: GHSA-c5f8-35qr-q4fm
CVE: CVE-2021-21333
CWE: CWE-74, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-26
Source: https://github.com/advisories/GHSA-c5f8-35qr-q4fm
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.27.0

## Details
### Impact
The notification emails sent for notifications for missed messages or for an expiring account are subject to HTML injection. In the case of the notification for missed messages, this could allow an attacker to insert forged content into the email.

The account expiry feature is not enabled by default and the HTML injection is not controllable by an attacker.

### Patches
This issue is fixed in #9200.

### Workarounds
For the missed messages notifications:

The `notif.html`, `notif_mail.html`, and `room.html` templates can be overridden with custom templates that manually escapes the variables using [JInja2's `escape` filter](https://jinja.palletsprojects.com/en/2.11.x/templates/#escape). See the `email.template_dir` setting.

For the account expiry notifications:

1. Account expiry can be disabled via the `account_validity.enabled` setting.

2. The `notice_expiry.html` template can be overridden with a custom template that manually escapes the variables using [JInja2's `escape` filter](https://jinja.palletsprojects.com/en/2.11.x/templates/#escape). See the `email.template_dir` setting.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-c5f8-35qr-q4fm
- https://nvd.nist.gov/vuln/detail/CVE-2021-21333
- https://github.com/matrix-org/synapse/pull/9200
- https://github.com/matrix-org/synapse/commit/e54746bdf7d5c831eabe4dcea76a7626f1de73df
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.27.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-134.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY
