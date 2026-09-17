# [H] Reddit Terminal Viewer (RTV) vulnerable to argument injection attacks

## Summary
Severity: High
Advisory: GHSA-336h-q7mh-8vf8
CVE: CVE-2017-17516
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-336h-q7mh-8vf8
Type: github-advisory

## Affected
- PyPI: `rtv` — affected >=0

## Details
scripts/inspect_webbrowser.py in Reddit Terminal Viewer (RTV) 1.19.0 does not validate strings before launching the program specified by the BROWSER environment variable, which might allow remote attackers to conduct argument-injection attacks via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17516
- https://github.com/michael-lazar/rtv/issues/531
- https://github.com/michael-lazar/rtv
- https://security-tracker.debian.org/tracker/CVE-2017-17516
