# [M] Python-Markdown has an Uncaught Exception

## Summary
Severity: Medium
Advisory: GHSA-5wmx-573v-2qwq
CVE: CVE-2025-69534
CWE: CWE-248, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-5wmx-573v-2qwq
Type: github-advisory

## Affected
- PyPI: `Markdown` — affected >=0 <3.8.1

## Details
Python-Markdown version 3.8 contain a vulnerability where malformed HTML-like sequences can cause html.parser.HTMLParser to raise an unhandled AssertionError during Markdown parsing. Because Python-Markdown does not catch this exception, any application that processes attacker-controlled Markdown may crash. This enables remote, unauthenticated Denial of Service in web applications, documentation systems, CI/CD pipelines, and any service that renders untrusted Markdown. The issue was acknowledged by the vendor and fixed in version 3.8.1. This issue causes a remote Denial of Service in any application parsing untrusted Markdown, and can lead to Information Disclosure through uncaught exceptions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69534
- https://github.com/Python-Markdown/markdown/issues/1534
- https://github.com/Python-Markdown/markdown/pull/1535
- https://github.com/Python-Markdown/markdown
- https://github.com/Python-Markdown/markdown/actions/runs/15736122892
- https://github.com/pypa/advisory-database/tree/main/vulns/markdown/PYSEC-2026-89.yaml
- http://www.openwall.com/lists/oss-security/2026/03/06/4
