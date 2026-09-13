# [C] Google Agent Development Kit (ADK) has a Code Injection and Missing Authentication vulnerability

## Summary
Severity: Critical
Advisory: GHSA-rg7c-g689-fr3x
CVE: CVE-2026-4810
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P/U:Amber (CVSS_V4)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-rg7c-g689-fr3x
Type: github-advisory

## Affected
- PyPI: `google-adk` — affected >=1.7.0 <1.28.1
- PyPI: `google-adk` — affected >=2.0.0a1 <2.0.0a2

## Details
A Code Injection and Missing Authentication vulnerability in Google Agent Development Kit (ADK) versions 1.7.0 (and 2.0.0a1) through 1.28.1 (and 2.0.0a2) on Python (OSS), Cloud Run, and GKE allows an unauthenticated remote attacker to execute arbitrary code on the server hosting the ADK instance.

This vulnerability was patched in versions 1.28.1 and 2.0.0a2.


Customers need to redeploy the upgraded ADK to their production environments. In addition, if they are running ADK Web locally, they also need to upgrade their local instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4810
- https://github.com/google/adk-python
- https://github.com/google/adk-python/blob/main/CHANGELOG.md#1274-2026-03-26
