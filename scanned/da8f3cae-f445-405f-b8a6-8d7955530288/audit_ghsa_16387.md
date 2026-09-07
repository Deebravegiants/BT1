# [M] Ghost has possible Cross-site Scripting issue

## Summary
Severity: Medium
Advisory: GHSA-99vc-xw8j-phjm
CVE: CVE-2024-23724
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-02-11
Source: https://github.com/advisories/GHSA-99vc-xw8j-phjm
Type: github-advisory

## Affected
- npm: `ghost` — affected >=0
- npm: `ghost` — affected >=0

## Details
Ghost through 5.76.0 allows stored XSS, and resultant privilege escalation in which a contributor can take over any account, via an SVG profile picture that contains JavaScript code to interact with the API on localhost TCP port 3001. NOTE: The discoverer reports that "The vendor does not view this as a valid vector."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23724
- https://github.com/TryGhost/Ghost/pull/19646
- https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2024-23724
- https://github.com/TryGhost/Ghost
- https://rhinosecuritylabs.com/blog
