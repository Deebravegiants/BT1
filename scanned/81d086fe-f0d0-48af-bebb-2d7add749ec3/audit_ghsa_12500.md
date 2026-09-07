# [M] Reflected XSS Vulnerability in dpaste

## Summary
Severity: Medium
Advisory: GHSA-r8j9-5cj7-cv39
CVE: CVE-2023-49277
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-01
Source: https://github.com/advisories/GHSA-r8j9-5cj7-cv39
Type: github-advisory

## Affected
- PyPI: `Dpaste` — affected >=0 <3.8

## Details
### Impact
A security vulnerability has been identified in the expires parameter of the dpaste API, allowing for a POST Reflected XSS attack. This vulnerability can be exploited by an attacker to execute arbitrary JavaScript code in the context of a user's browser, potentially leading to unauthorized access, data theft, or other malicious activities.

### Patches
- A patch has been applied to the dpaste GitHub repository to address the specific content value injection vulnerability.
- Users are strongly advised to upgrade to dpaste release v3.8 or later versions, as dpaste versions older than v3.8 are susceptible to the identified security vulnerability.
- The patch can be viewed and applied from the following link: [dpaste Commit Patch](https://github.com/DarrenOfficial/dpaste/commit/44a666a79b3b29ed4f340600bfcf55113bfb7086.patch)

### Workarounds
At this time, the recommended course of action is to apply the provided patch to the affected systems. No known workarounds have been identified, and applying the patch is the most effective way to remediate the vulnerability.

## References
- https://github.com/DarrenOfficial/dpaste/security/advisories/GHSA-r8j9-5cj7-cv39
- https://nvd.nist.gov/vuln/detail/CVE-2023-49277
- https://github.com/DarrenOfficial/dpaste/commit/44a666a79b3b29ed4f340600bfcf55113bfb7086
- https://github.com/DarrenOfficial/dpaste
