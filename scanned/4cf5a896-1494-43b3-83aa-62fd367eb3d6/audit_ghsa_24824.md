# [M] Regular expression denial of service in url_regex

## Summary
Severity: Medium
Advisory: GHSA-hg3w-7hj9-m3f7
CVE: CVE-2022-21195
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-21
Source: https://github.com/advisories/GHSA-hg3w-7hj9-m3f7
Type: github-advisory

## Affected
- PyPI: `url_regex` — affected >=0

## Details
All versions of package url-regex are vulnerable to Regular Expression Denial of Service (ReDoS) which can cause the CPU usage to crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21195
- https://github.com/AlexFlipnote/url_regex
- https://github.com/AlexFlipnote/url_regex/blob/master/url_regex/url_regex.py
- https://snyk.io/vuln/SNYK-PYTHON-URLREGEX-2347643
