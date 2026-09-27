# [C] WSO2 API Manager XML External Entity (XXE) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h94w-8qhg-3xmc
CVE: CVE-2025-2905
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2025-05-05
Source: https://github.com/advisories/GHSA-h94w-8qhg-3xmc
Type: github-advisory

## Affected
- Maven: `org.wso2.am:am-distribution-parent` — affected >=0 <2.1.0

## Details
An XML External Entity (XXE) vulnerability exists in the gateway component of WSO2 API Manager due to insufficient validation of XML input in crafted URL paths. User-supplied XML is parsed without appropriate restrictions, enabling external entity resolution.

This vulnerability can be exploited by an unauthenticated remote attacker to read files from the server’s filesystem or perform denial-of-service (DoS) attacks.

  *  On systems running JDK 7 or early JDK 8, full file contents may be exposed.

  *  On later versions of JDK 8 and newer, only the first line of a file may be read, due to improvements in XML parser behavior.

  *  DoS attacks such as "Billion Laughs" payloads can cause service disruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2905
- https://github.com/wso2/product-apim
- https://security.docs.wso2.com/en/latest/security-announcements/security-advisories/2025/WSO2-2025-3993
