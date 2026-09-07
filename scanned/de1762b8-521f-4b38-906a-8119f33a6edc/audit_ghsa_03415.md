# [M] Exposure of class information in RESTEasy

## Summary
Severity: Medium
Advisory: GHSA-244r-fcj3-ghjq
CVE: CVE-2021-20289
CWE: CWE-209, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-244r-fcj3-ghjq
Type: github-advisory

## Affected
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=4.6.0 <4.6.1
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=4.0.0 <4.5.10
- Maven: `org.jboss.resteasy:resteasy-core` — affected >=3.0.0 <3.16.0

## Details
A flaw was found in RESTEasy in all current versions of RESTEasy up to 4.6.0.Final. The endpoint class and method names are returned as part of the exception response when RESTEasy cannot convert one of the request URI path or query values to the matching JAX-RS resource method's parameter value. The highest threat from this vulnerability is to data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20289
- https://bugzilla.redhat.com/show_bug.cgi?id=1935927
- https://bugzilla.redhat.com/show_bug.cgi?id=1941544
- https://issues.redhat.com/browse/RESTEASY-2843
- https://security.netapp.com/advisory/ntap-20210528-0008
- https://www.oracle.com/security-alerts/cpuapr2022.html
