# [M] Jinja has a sandbox breakout through indirect reference to format method

## Summary
Severity: Medium
Advisory: GHSA-q2x7-8rv6-6q7h
CVE: CVE-2024-56326
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-q2x7-8rv6-6q7h
Type: github-advisory

## Affected
- PyPI: `jinja2` — affected >=0 <3.1.5

## Details
An oversight in how the Jinja sandboxed environment detects calls to `str.format` allows an attacker that controls the content of a template to execute arbitrary Python code.

To exploit the vulnerability, an attacker needs to control the content of a template. Whether that is the case depends on the type of application using Jinja. This vulnerability impacts users of applications which execute untrusted templates.

Jinja's sandbox does catch calls to `str.format` and ensures they don't escape the sandbox. However, it's possible to store a reference to a malicious string's `format` method, then pass that to a filter that calls it. No such filters are built-in to Jinja, but could be present through custom filters in an application. After the fix, such indirect calls are also handled by the sandbox.

## References
- https://github.com/pallets/jinja/security/advisories/GHSA-q2x7-8rv6-6q7h
- https://nvd.nist.gov/vuln/detail/CVE-2024-56326
- https://github.com/pallets/jinja/commit/48b0687e05a5466a91cd5812d604fa37ad0943b4
- https://github.com/pallets/jinja
- https://github.com/pallets/jinja/releases/tag/3.1.5
- https://lists.debian.org/debian-lts-announce/2025/04/msg00022.html
