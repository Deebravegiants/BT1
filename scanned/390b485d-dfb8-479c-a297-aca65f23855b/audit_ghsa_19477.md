# [M] XSS in the /files Endpoint of the Generic REST API

## Summary
Severity: Medium
Advisory: GHSA-88h5-34xw-2q56
CVE: CVE-2025-32960
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-88h5-34xw-2q56
Type: github-advisory

## Affected
- Maven: `com.haulmont.addon.restapi:restapi-rest-api` — affected >=0 <7.2.7

## Details
### Impact

The input parameter, which consists of a file path and name, can be manipulated to return the Content-Type header with text/html if the name part ends with .html. This could allow malicious JavaScript code to be executed in the browser. For a successful attack, a malicious file needs to be uploaded beforehand.

The severity of the vulnerability is mitigated by the fact that the application UI and the generic REST API are typically accessible only to authenticated users.

### Patches

The problem has been fixed in CUBA REST API add-on 7.2.7.

### Workarounds

A workaround for those who are unable to upgrade: [Disable Files Endpoint in CUBA Application](https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-cuba-application).

### References

[Files Functionality Vulnerabilities :: Jmix Documentation](https://docs.jmix.io/jmix/files-vulnerabilities.html)

Similar vulnerability in Jmix: [XSS in the /files Endpoint of the Generic REST API · Advisory · jmix-framework/jmix](https://github.com/jmix-framework/jmix/security/advisories/GHSA-x27v-f838-jh93)

## References
- https://github.com/cuba-platform/restapi/security/advisories/GHSA-88h5-34xw-2q56
- https://github.com/jmix-framework/jmix/security/advisories/GHSA-x27v-f838-jh93
- https://nvd.nist.gov/vuln/detail/CVE-2025-32960
- https://github.com/cuba-platform/restapi/commit/b3d599f6657d7e212fdb134a61ab5e0888669eb1
- https://docs.jmix.io/jmix/files-vulnerabilities.html
- https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-cuba-application
- https://github.com/cuba-platform/restapi
