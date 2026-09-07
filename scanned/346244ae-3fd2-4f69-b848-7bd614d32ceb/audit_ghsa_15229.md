# [M] Jinja vulnerable to HTML attribute injection when passing user input as keys to xmlattr filter

## Summary
Severity: Medium
Advisory: GHSA-h5c8-rqwp-cp95
CVE: CVE-2024-22195
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-11
Source: https://github.com/advisories/GHSA-h5c8-rqwp-cp95
Type: github-advisory

## Affected
- PyPI: `jinja2` — affected >=0 <3.1.3

## Details
The `xmlattr` filter in affected versions of Jinja accepts keys containing spaces. XML/HTML attributes cannot contain spaces, as each would then be interpreted as a separate attribute. If an application accepts keys (as opposed to only values) as user input, and renders these in pages that other users see as well, an attacker could use this to inject other attributes and perform XSS. Note that accepting keys as user input is not common or a particularly intended use case of the `xmlattr` filter, and an application doing so should already be verifying what keys are provided regardless of this fix.

## References
- https://github.com/pallets/jinja/security/advisories/GHSA-h5c8-rqwp-cp95
- https://nvd.nist.gov/vuln/detail/CVE-2024-22195
- https://github.com/pallets/jinja/commit/716795349a41d4983a9a4771f7d883c96ea17be7
- https://github.com/pallets/jinja
- https://github.com/pallets/jinja/releases/tag/3.1.3
- https://lists.debian.org/debian-lts-announce/2024/01/msg00010.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5XCWZD464AJJJUBOO7CMPXQ4ROBC6JX2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DELCVUUYX75I5K4Q5WMJG4MUZJA6VAIP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O7YWRBX6JQCWC2XXCTZ55C7DPMGICCN3
