# [M] Grails data binding causes JVM crash and/or other denial of service

## Summary
Severity: Medium
Advisory: GHSA-3pjv-r7w4-2cf5
CVE: CVE-2023-46131
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-20
Source: https://github.com/advisories/GHSA-3pjv-r7w4-2cf5
Type: github-advisory

## Affected
- Maven: `org.grails:grails-databinding` — affected >=6.0.0 <6.1.0
- Maven: `org.grails:grails-databinding` — affected >=5.0.0 <5.3.4
- Maven: `org.grails:grails-databinding` — affected >=4.0.0 <4.1.3
- Maven: `org.grails:grails-databinding` — affected >=2.0.0 <3.3.17

## Details
### Impact
A specially crafted web request can lead to a JVM crash or denial of service. Any Grails framework application using Grails data binding is vulnerable.

### Patches
Patches are available for Grails 3 and later.

### Workarounds
No workaround is possible except to avoid data binding to request data.

### References

- [Blog post](https://grails.org/blog/2023-12-20-cve-data-binding-dos.html)
- [Discussion](https://github.com/grails/grails-core/issues/13302)
- [Mitre CVD record](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-46131)

## References
- https://github.com/grails/grails-core/security/advisories/GHSA-3pjv-r7w4-2cf5
- https://nvd.nist.gov/vuln/detail/CVE-2023-46131
- https://github.com/grails/grails-core/issues/13302
- https://github.com/grails/grails-core/commit/74326bdd2cf7dcb594092165e9464520f8366c60
- https://github.com/grails/grails-core/commit/c401faaa6c24c021c758b95f72304a0e855a8db3
- https://github.com/grails/grails-core
- https://grails.org/blog/2023-12-20-cve-data-binding-dos.html
