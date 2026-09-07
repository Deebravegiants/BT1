# [C] Grails framework Remote Code Execution via Data Binding

## Summary
Severity: Critical
Advisory: GHSA-6rh6-x8ww-9h97
CVE: CVE-2022-35912
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-21
Source: https://github.com/advisories/GHSA-6rh6-x8ww-9h97
Type: github-advisory

## Affected
- Maven: `org.grails:grails-databinding` — affected >=3.3.10 <3.3.15
- Maven: `org.grails:grails-databinding` — affected >=4.0.0 <4.1.1
- Maven: `org.grails:grails-databinding` — affected >=5.0.0 <5.1.9
- Maven: `org.grails:grails-databinding` — affected >=5.2.0 <5.2.1

## Details
### Impact
A vulnerability has been discovered in the Grails data-binding logic which allows for Remote Code Execution in a Grails application. This exploit requires the application to be running on Java 8, either deployed as a WAR to a servlet container, or an executable JAR.  

### Patches
Grails framework versions 5.2.1, 5.1.9, 4.1.1, and 3.3.15

### References
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-35912
https://grails.org/blog/2022-07-18-rce-vulnerability.html

### For more information
If you have any questions or comments about this advisory:
* https://grails.org/blog/2022-07-18-rce-vulnerability.html
*  https://github.com/grails/grails-core/issues/12626
* Email us at [info@grails.org](mailto:info@grails.org)

### Credit

This vulnerability was discovered by  [meizjm3i](https://github.com/meizjm3i) and [codeplutos](https://github.com/codeplutos) of AntGroup FG Security Lab

## References
- https://github.com/grails/grails-core/security/advisories/GHSA-6rh6-x8ww-9h97
- https://nvd.nist.gov/vuln/detail/CVE-2022-35912
- https://github.com/grails/grails-core/issues/12626
- https://github.com/grails/grails-core
- https://grails.org/blog/2022-07-18-rce-vulnerability.html
- http://www.openwall.com/lists/oss-security/2022/07/20/4
