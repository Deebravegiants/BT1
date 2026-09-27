# [H] Path traversal in the OWASP Enterprise Security API

## Summary
Severity: High
Advisory: GHSA-8m5h-hrqm-pxm2
CVE: CVE-2022-23457
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-27
Source: https://github.com/advisories/GHSA-8m5h-hrqm-pxm2
Type: github-advisory

## Affected
- Maven: `org.owasp.esapi:esapi` — affected >=0 <2.3.0.0

## Details
### Impact
The default implementation of `Validator.getValidDirectoryPath(String, String, File, boolean)` may incorrectly treat the tested input string as a child of the specified parent directory. This potentially could allow control-flow bypass checks to be defeated if an attack can specify the entire string representing the 'input' path.

### Patches
This vulnerability is patched in release 2.3.0.0 of ESAPI. See https://github.com/ESAPI/esapi-java-legacy/releases/tag/esapi-2.3.0.0 for details.

### Workarounds
Yes; in theory, one _could_ write the own implementation of the Validator interface. This would most easily be done by sub-classing a version of the affected `DefaultValidator` class and then overriding the affected `getValidDirectoryPath()` to correct the issue. However, this is not recommended.


### For more information
If you have any questions or comments about this advisory:
* Email one of the project co-leaders. See email addresses listed on  the [OWASP ESAPI wiki](https://owasp.org/www-project-enterprise-security-api/) page, under "Leaders".
* Send email to one of the two ESAPI related Google Groups listed under [Where to Find More Information on ESAPI](https://github.com/ESAPI/esapi-java-legacy#where-to-find-more-information-on-esapi) on our [README.md](https://github.com/ESAPI/esapi-java-legacy#readme) page.

## References
- https://github.com/ESAPI/esapi-java-legacy/security/advisories/GHSA-8m5h-hrqm-pxm2
- https://nvd.nist.gov/vuln/detail/CVE-2022-23457
- https://github.com/ESAPI/esapi-java-legacy/commit/a0d67b75593878b1b6e39e2acc1773b3effedb2a
- https://github.com/ESAPI/esapi-java-legacy
- https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/GHSL-2022-008_The_OWASP_Enterprise_Security_API.md
- https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/esapi4java-core-2.3.0.0-release-notes.txt
- https://lists.debian.org/debian-lts-announce/2025/07/msg00010.html
- https://security.netapp.com/advisory/ntap-20230127-0014
- https://securitylab.github.com/advisories/GHSL-2022-008_The_OWASP_Enterprise_Security_API
- https://www.oracle.com/security-alerts/cpujul2022.html
