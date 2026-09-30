# [H] git-url-parse Regular Expression Denial of Service

## Summary
Severity: High
Advisory: GHSA-4xqq-73wg-5mjp
CVE: CVE-2023-32758
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-15
Source: https://github.com/advisories/GHSA-4xqq-73wg-5mjp
Type: github-advisory

## Affected
- PyPI: `git-url-parse` — affected >=0

## Details
giturlparse (aka git-url-parse) through 1.2.2, as used in Semgrep 1.5.2 through 1.24.1, is vulnerable to ReDoS (Regular Expression Denial of Service) if parsing untrusted URLs. This might be relevant if Semgrep is analyzing an untrusted package (for example, to check whether it accesses any Git repository at an http:// URL), and that package's author placed a ReDoS attack payload in a URL used by the package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32758
- https://github.com/returntocorp/semgrep/pull/7611
- https://github.com/returntocorp/semgrep/pull/7943
- https://github.com/returntocorp/semgrep/pull/7955
- https://github.com/coala/git-url-parse
- https://github.com/coala/git-url-parse/blob/master/giturlparse/parser.py#L53
- https://pypi.org/project/git-url-parse
