# [M] Reflected Cross-Site Scripting (XSS) in zenml

## Summary
Severity: Medium
Advisory: GHSA-3434-hc3m-8mmm
CVE: CVE-2024-5062
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-30
Source: https://github.com/advisories/GHSA-3434-hc3m-8mmm
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0.57.1 <0.58.0

## Details
A reflected Cross-Site Scripting (XSS) vulnerability was identified in zenml-io/zenml version 0.57.1. The vulnerability exists due to improper neutralization of input during web page generation, specifically within the survey redirect parameter. This flaw allows an attacker to redirect users to a specified URL after completing a survey, without proper validation of the 'redirect' parameter. Consequently, an attacker can execute arbitrary JavaScript code in the context of the user's browser session. This vulnerability could be exploited to steal cookies, potentially leading to account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5062
- https://github.com/zenml-io/zenml/commit/21edd863c0ba53c1110b6f018a07c2d6853cf6d4
- https://github.com/pypa/advisory-database/tree/main/vulns/zenml/PYSEC-2024-176.yaml
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/ceddd3c1-a9da-4d6c-85c4-41d4d1e1102f
