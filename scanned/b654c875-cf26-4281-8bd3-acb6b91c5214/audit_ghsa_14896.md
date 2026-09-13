# [M] Improper line feed handling in zenml

## Summary
Severity: Medium
Advisory: GHSA-7gjr-hcc3-xfr4
CVE: CVE-2024-4460
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-06-24
Source: https://github.com/advisories/GHSA-7gjr-hcc3-xfr4
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0 <0.57.1

## Details
A denial of service (DoS) vulnerability exists in zenml-io/zenml version 0.56.3 due to improper handling of line feed (`\n`) characters in component names. When a low-privileged user adds a component through the API endpoint `api/v1/workspaces/default/components` with a name containing a `\n` character, it leads to uncontrolled resource consumption. This vulnerability results in the inability of users to add new components in certain categories (e.g., 'Image Builder') and to register new stacks through the UI, thereby degrading the user experience and potentially rendering the ZenML Dashboard unusable. The issue does not affect component addition through the Web UI, as `\n` characters are properly escaped in that context. The vulnerability was tested on ZenML running in Docker, and it was observed in both Firefox and Chrome browsers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4460
- https://github.com/zenml-io/zenml/commit/164cc09032060bbfc17e9dbd62c13efd5ff5771b
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/a387c935-b970-44d7-bddc-71c1c90aa2de
