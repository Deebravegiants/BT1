# [M] Qutebrowser XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m4fw-77v7-924m
CVE: CVE-2018-1000559
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-09-13
Source: https://github.com/advisories/GHSA-m4fw-77v7-924m
Type: github-advisory

## Affected
- PyPI: `qutebrowser` — affected >=0.11.0 <1.3.3

## Details
qutebrowser version introduced in v0.11.0 ([1179ee7a937fb31414d77d9970bac21095358449](https://github.com/qutebrowser/qutebrowser/commit/5a7869f2feaa346853d2a85413d6527c87ef0d9f)) contains a Cross Site Scripting (XSS) vulnerability in history command, `qute://history` page that can result in Via injected JavaScript code, a website can steal the user's browsing history. This attack appear to be exploitable via the victim must open a page with a specially crafted `<title>` attribute, and then open the `qute://history` site via the `:history` command. This vulnerability appears to have been fixed in fixed in v1.3.3 ([4c9360237f186681b1e3f2a0f30c45161cf405c7](https://github.com/qutebrowser/qutebrowser/commit/4c9360237f186681b1e3f2a0f30c45161cf405c7), to be released today) and v1.4.0 ([5a7869f2feaa346853d2a85413d6527c87ef0d9f](https://github.com/qutebrowser/qutebrowser/commit/5a7869f2feaa346853d2a85413d6527c87ef0d9f), released later this week).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000559
- https://github.com/qutebrowser/qutebrowser/issues/4011
- https://github.com/qutebrowser/qutebrowser/commit/4c9360237f186681b1e3f2a0f30c45161cf405c7
- https://github.com/qutebrowser/qutebrowser/commit/5a7869f2feaa346853d2a85413d6527c87ef0d9f
- https://github.com/advisories/GHSA-m4fw-77v7-924m
- https://github.com/pypa/advisory-database/tree/main/vulns/qutebrowser/PYSEC-2018-26.yaml
- https://github.com/qutebrowser/qutebrowser
