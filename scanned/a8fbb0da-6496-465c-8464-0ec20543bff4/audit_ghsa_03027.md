# [H] Reflected Cross-site Scripting in ACS Commons

## Summary
Severity: High
Advisory: GHSA-f92j-qf46-p6vm
CVE: CVE-2021-21028
CWE: CWE-416, CWE-79
Ecosystem: Maven
Published: 2021-02-02
Source: https://github.com/advisories/GHSA-f92j-qf46-p6vm
Type: github-advisory

## Affected
- Maven: `com.adobe.acs:acs-aem-commons` — affected >=0 <4.10.0

## Details
### Impact

ACS Commons version 4.9.2 (and earlier) suffers from a Reflected Cross-site Scripting (XSS) vulnerability in version-compare and page-compare due to invalid JCR characters that are not handled correctly.

An attacker could potentially exploit this vulnerability to inject malicious JavaScript content into vulnerable form fields and execute it within the context of the victim's browser. Exploitation of this issue requires user interaction in order to be successful.

### Patches

This issue has been resolved in v4.10.0

### Workarounds

No workaround exist.

### References

N/A

### For more information

If you have any questions or comments about this advisory open an issue in acs-aem-commons.

### Credit

This issue was discovered and reported by Christopher Whipp (Christopher.Whipp@servicesaustralia.gov.au).

## References
- https://github.com/Adobe-Consulting-Services/acs-aem-commons/security/advisories/GHSA-f92j-qf46-p6vm
- https://nvd.nist.gov/vuln/detail/CVE-2021-21028
- https://github.com/Adobe-Consulting-Services/acs-aem-commons/commit/14d769c86606c4ce9a93c47a19f87e1ad72788d6
- https://helpx.adobe.com/security/products/acrobat/apsb21-09.html
