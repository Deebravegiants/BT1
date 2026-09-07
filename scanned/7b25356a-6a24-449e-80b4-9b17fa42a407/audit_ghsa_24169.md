# [M] Cross-site Scripting in Jolokia agent

## Summary
Severity: Medium
Advisory: GHSA-hfpg-gqjw-779m
CVE: CVE-2018-1000129
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hfpg-gqjw-779m
Type: github-advisory

## Affected
- Maven: `org.jolokia:jolokia-core` — affected >=1.3.7 <1.5.0

## Details
An XSS vulnerability exists in the Jolokia agent version 1.3.7 in the HTTP servlet that allows an attacker to execute malicious javascript in the victim's browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000129
- https://github.com/rhuss/jolokia/commit/5895d5c137c335e6b473e9dcb9baf748851bbc5f#diff-f19898247eddb55de6400489bff748ad
- https://access.redhat.com/errata/RHSA-2018:2669
- https://access.redhat.com/errata/RHSA-2018:3817
- https://github.com/rhuss/jolokia
- https://github.com/rhuss/jolokia/releases/tag/v1.5.0
- https://jolokia.org/#Security_fixes_with_1.5.0
