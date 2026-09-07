# [M] XSS in the /download Endpoint of the JPA Web API

## Summary
Severity: Medium
Advisory: GHSA-hg25-w3vg-7279
CVE: CVE-2025-32961
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-hg25-w3vg-7279
Type: github-advisory

## Affected
- Maven: `com.haulmont.addon.jpawebapi:jpawebapi-jpawebapi` — affected >=0 <1.1.1

## Details
### Impact

The input parameter, which consists of a file path and name, can be manipulated to return the Content-Type header with text/html if the name part ends with .html. This could allow malicious JavaScript code to be executed in the browser. For a successful attack, a malicious file needs to be uploaded beforehand.

The severity of the vulnerability is mitigated by the fact that the application UI and the JPA Web API are typically accessible only to authenticated users.

### Patches

The problem has been fixed in CUBA JPA Web API add-on 1.1.1.

### Workarounds

A workaround for those who are unable to upgrade: [Disable Files Endpoint in CUBA Application](https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-cuba-application).

### References

[Files Functionality Vulnerabilities :: Jmix Documentation](https://docs.jmix.io/jmix/files-vulnerabilities.html)

Similar vulnerability in Jmix: [XSS in the /files Endpoint of the Generic REST API · Advisory · jmix-framework/jmix](https://github.com/jmix-framework/jmix/security/advisories/GHSA-x27v-f838-jh93)

## References
- https://github.com/cuba-platform/jpawebapi/security/advisories/GHSA-hg25-w3vg-7279
- https://github.com/jmix-framework/jmix/security/advisories/GHSA-x27v-f838-jh93
- https://nvd.nist.gov/vuln/detail/CVE-2025-32961
- https://github.com/cuba-platform/jpawebapi/commit/78b837d7e2b12d0df69cef1bc6042ebf3bdaf22c
- https://docs.jmix.io/jmix/files-vulnerabilities.html
- https://docs.jmix.io/jmix/files-vulnerabilities.html#disable-files-endpoint-in-cuba-application
- https://github.com/cuba-platform/jpawebapi
