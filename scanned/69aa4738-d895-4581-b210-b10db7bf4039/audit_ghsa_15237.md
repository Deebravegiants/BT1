# [M] Follow Redirects improperly handles URLs in the url.parse() function

## Summary
Severity: Medium
Advisory: GHSA-jchw-25xp-jwwc
CVE: CVE-2023-26159
CWE: CWE-20, CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-02
Source: https://github.com/advisories/GHSA-jchw-25xp-jwwc
Type: github-advisory

## Affected
- npm: `follow-redirects` — affected >=0 <1.15.4

## Details
Versions of the package follow-redirects before 1.15.4 are vulnerable to Improper Input Validation due to the improper handling of URLs by the url.parse() function. When new URL() throws an error, it can be manipulated to misinterpret the hostname. An attacker could exploit this weakness to redirect traffic to a malicious site, potentially leading to information disclosure, phishing attacks, or other security breaches.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26159
- https://github.com/follow-redirects/follow-redirects/issues/235
- https://github.com/follow-redirects/follow-redirects/pull/236
- https://github.com/follow-redirects/follow-redirects/commit/7a6567e16dfa9ad18a70bfe91784c28653fbf19d
- https://github.com/follow-redirects/follow-redirects
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZZ425BFKNBQ6AK7I5SAM56TWON5OF2XM
- https://security.netapp.com/advisory/ntap-20241108-0002
- https://security.snyk.io/vuln/SNYK-JS-FOLLOWREDIRECTS-6141137
