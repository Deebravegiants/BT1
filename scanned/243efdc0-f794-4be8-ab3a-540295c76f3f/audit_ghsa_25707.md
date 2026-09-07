# [M] Cross-site Scripting in org.owasp.esapi:esapi

## Summary
Severity: Medium
Advisory: GHSA-q77q-vx4q-xx6q
CVE: CVE-2022-24891
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-27
Source: https://github.com/advisories/GHSA-q77q-vx4q-xx6q
Type: github-advisory

## Affected
- Maven: `org.owasp.esapi:esapi` — affected >=0 <2.3.0.0

## Details
### Impact
There is a potential for an XSS vulnerability in ESAPI caused by a incorrect regular expression for "onsiteURL" in the **antisamy-esapi.xml** configuration file that can cause URLs with the "javascript:" scheme to NOT be sanitized. See the reference below for full details.

### Patches
Patched in ESAPI 2.3.0.0 and later. See important remediation details in the reference given below.

### Workarounds
Manually edit your **antisamy-esapi.xml** configuration files to change the "onsiteURL" regular expression as per remediation instructions in the reference below.

### References
[Security Bulletin 8](https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/ESAPI-security-bulletin8.pdf)

### For more information
If you have any questions or comments about this advisory:
* Email one of the project co-leaders. See email addresses listed on  the [OWASP ESAPI wiki](https://owasp.org/www-project-enterprise-security-api/) page, under "Leaders".
* Send email to one of the two ESAPI related Google Groups listed under [Where to Find More Information on ESAPI](https://github.com/ESAPI/esapi-java-legacy#where-to-find-more-information-on-esapi) on our [README.md](https://github.com/ESAPI/esapi-java-legacy#readme) page.

## References
- https://github.com/ESAPI/esapi-java-legacy/security/advisories/GHSA-q77q-vx4q-xx6q
- https://nvd.nist.gov/vuln/detail/CVE-2022-24891
- https://github.com/ESAPI/esapi-java-legacy
- https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/ESAPI-security-bulletin8.pdf
- https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/esapi4java-core-2.3.0.0-release-notes.txt
- https://lists.debian.org/debian-lts-announce/2025/07/msg00010.html
- https://security.netapp.com/advisory/ntap-20230127-0014
- https://www.oracle.com/security-alerts/cpujul2022.html
