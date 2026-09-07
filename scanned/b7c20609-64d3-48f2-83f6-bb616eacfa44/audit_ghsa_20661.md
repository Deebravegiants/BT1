# [M] AEM WCM Core Components CVG Image vulnerable to Reflected Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-qcgc-6q86-7x2p
CVE: CVE-2022-35697
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-11
Source: https://github.com/advisories/GHSA-qcgc-6q86-7x2p
Type: github-advisory

## Affected
- Maven: `com.adobe.cq:core.wcm.components.core` — affected >=0 <2.20.8

## Details
Core Components version 2.20.6 (and earlier) suffer from a reflected cross-site scripting (XSS) vulnerability in `AdaptiveImageServlet` via SVG images. An attacker with author access can upload a special crafted SVG image (including a malicious Javascript) and obtain a link that, when loaded by another authenticated users, will execute the malicious script and gain access to other user's session. The issue has been resolved in 2.20.8. There are currently no known workarounds.

## References
- https://github.com/adobe/aem-core-wcm-components/security/advisories/GHSA-qcgc-6q86-7x2p
- https://nvd.nist.gov/vuln/detail/CVE-2022-35697
- https://github.com/adobe/aem-core-wcm-components
