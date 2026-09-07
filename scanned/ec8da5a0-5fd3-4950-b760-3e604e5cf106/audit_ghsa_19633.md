# [M] CodeChecker open redirect when URL contains multiple slashes after the product name

## Summary
Severity: Medium
Advisory: GHSA-g839-x3p3-g5fm
CVE: CVE-2025-1300
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-g839-x3p3-g5fm
Type: github-advisory

## Affected
- PyPI: `codechecker` — affected >=0 <6.24.6

## Details
Summary
---

CodeChecker versions up to 6.24.5 contain an open redirect vulnerability due to missing protections against multiple slashes after the product name in the URL's path segment.  This results in bypassing protections against CVE-2021-28861, leading to the same open redirect pathway.

Details
---

CodeChecker processes GET requests by first rewriting the path segment of the URL, and then passing the rewritten URL to the webserver framework.
When trimming the product name from the URL, no sanitization was performed on the remaining URL, which reintroduced the same issue as CVE-2021-28861, leading to the same open redirect pathway using URLs such as `/Default//attacker.com/%2f..`.

Impact
---

The vulnerability allows an attacker to create a hyperlink that looks like a legitimate CodeChecker URL, but redirects to an attacker-supplied website when clicked.

## References
- https://github.com/Ericsson/codechecker/security/advisories/GHSA-g839-x3p3-g5fm
- https://nvd.nist.gov/vuln/detail/CVE-2025-1300
- https://github.com/Ericsson/codechecker
