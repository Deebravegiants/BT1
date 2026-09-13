# [H] Improper Privilege Management in Spring Framework

## Summary
Severity: High
Advisory: GHSA-gfwj-fwqj-fp3v
CVE: CVE-2021-22118
CWE: CWE-269, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gfwj-fwqj-fp3v
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=5.2.0 <5.2.15
- Maven: `org.springframework:spring-web` — affected >=5.3.0 <5.3.7

## Details
In Spring Framework, versions 5.2.x prior to 5.2.15 and versions 5.3.x prior to 5.3.7, a WebFlux application is vulnerable to a privilege escalation: by (re)creating the temporary storage directory, a locally authenticated malicious user can read or modify files that have been uploaded to the WebFlux application, or overwrite arbitrary files with multipart request data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22118
- https://github.com/spring-projects/spring-framework/issues/26931
- https://github.com/spring-projects/spring-framework/commit/0d0d75e25322d8161002d861fff3ec04ba8be5ac
- https://github.com/spring-projects/spring-framework/commit/cce60c479c22101f24b2b4abebb6d79440b120d1
- https://github.com/spring-projects/spring-framework
- https://security.netapp.com/advisory/ntap-20210713-0005
- https://spring.io/security/cve-2021-22118
- https://tanzu.vmware.com/security/cve-2021-22118
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
