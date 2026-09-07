# [M] HTML Injection in Froxlor

## Summary
Severity: Medium
Advisory: GHSA-j739-gw6q-f4c7
CVE: CVE-2020-29653
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-14
Source: https://github.com/advisories/GHSA-j739-gw6q-f4c7
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0

## Details
Froxlor through 0.10.22 does not perform validation on user input passed in the customermail GET parameter. The value of this parameter is reflected in the login webpage, allowing the injection of arbitrary HTML tags.

Note: Froxlor version 0.10.22 introduces AntiXSS cross-site scripting protection, but AntiXSS only provides partial protection for this particular issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29653
- https://github.com/Froxlor/Froxlor/commit/6bf5eccc2477257b6c1760a3c3784ae7e0554ce0
- https://github.com/Froxlor/Froxlor
- https://github.com/Froxlor/Froxlor/security/advisories
- https://nozero.io/en/cve-2020-29653-froxlor-html-injection-dangling-markup
