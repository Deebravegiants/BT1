# [M] Spring Framework DoS via conditional HTTP request

## Summary
Severity: Medium
Advisory: GHSA-2rmj-mq67-h97g
CVE: CVE-2024-38809
CWE: CWE-1333, CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-09-24
Source: https://github.com/advisories/GHSA-2rmj-mq67-h97g
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=0 <5.3.38
- Maven: `org.springframework:spring-web` — affected >=6.0.0 <6.0.23
- Maven: `org.springframework:spring-web` — affected >=6.1.0 <6.1.12

## Details
### Description
Applications that parse ETags from `If-Match` or `If-None-Match` request headers are vulnerable to DoS attack.

### Affected Spring Products and Versions
org.springframework:spring-web in versions 

6.1.0 through 6.1.11
6.0.0 through 6.0.22
5.3.0 through 5.3.37

Older, unsupported versions are also affected

### Mitigation
Users of affected versions should upgrade to the corresponding fixed version.
6.1.x -> 6.1.12
6.0.x -> 6.0.23
5.3.x -> 5.3.38
No other mitigation steps are necessary.

Users of older, unsupported versions could enforce a size limit on `If-Match` and `If-None-Match` headers, e.g. through a Filter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38809
- https://github.com/spring-projects/spring-framework/issues/33372
- https://github.com/spring-projects/spring-framework/commit/582bfccbb72e5c8959a0b472d1dc7d03a20520f3
- https://github.com/spring-projects/spring-framework/commit/8d16a50907c11f7e6b407d878a26e84eba08a533
- https://github.com/spring-projects/spring-framework/commit/bb17ad8314b81850a939fd265fb53b3361705e85
- https://github.com/spring-projects/spring-framework
- https://spring.io/security/cve-2024-38809
