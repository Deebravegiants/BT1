# [M] UnoPim Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hv6m-qj65-26q3
CVE: CVE-2024-50637
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-06
Source: https://github.com/advisories/GHSA-hv6m-qj65-26q3
Type: github-advisory

## Affected
- Packagist: `unopim/unopim` — affected >=0 <0.1.4

## Details
UnoPim 0.1.3 and below is vulnerable to Cross Site Scripting (XSS) in the Create User function.

The vulnerability allows attackers to perform XSS in SVG file extension, which can be used to stealing cookies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-50637
- https://github.com/unopim/unopim/issues/41
- https://github.com/unopim/unopim
- https://github.com/unopim/unopim/releases/tag/v0.1.4
- https://github.com/yamerooo123/ResearchNBugBountyEncyclopedia/blob/main/Researches/Unopim/Findings.md
